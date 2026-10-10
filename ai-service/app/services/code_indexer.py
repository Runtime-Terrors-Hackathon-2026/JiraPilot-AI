"""
Deterministic Source-Code Indexer & Static Analysis Engine for JiraPilot AI.
Extracts symbols, Spring MVC mappings, exception handlers, stack-trace coordinates,
and execution paths from local approved repository workspaces without external LLM dependencies.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.models.schemas import InspectedSymbol, ExecutionPathStep, FailureLocation

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent

def resolve_repo_path(repo_metadata: Dict[str, Any]) -> Optional[Path]:
    """Resolves the physical directory path for a configured repository."""
    local_path = repo_metadata.get("localPath")
    if local_path:
        p = WORKSPACE_ROOT / local_path
        if p.exists() and p.is_dir():
            return p
    
    # Fallback to display name in mock-repositories or root
    name = repo_metadata.get("displayName") or repo_metadata.get("serviceName")
    if name:
        cand = WORKSPACE_ROOT / "mock-repositories" / name
        if cand.exists() and cand.is_dir():
            return cand
    return None

def scan_repository_files(repo_path: Path) -> List[Path]:
    """Scans all source code and configuration files in the approved repository."""
    valid_exts = {".java", ".kt", ".py", ".ts", ".tsx", ".js", ".yml", ".yaml", ".json", ".xml"}
    found_files = []
    for root, _, files in os.walk(repo_path):
        for f in files:
            ext = Path(f).suffix.lower()
            if ext in valid_exts and not f.startswith("."):
                found_files.append(Path(root) / f)
    return found_files

def extract_file_lines(file_path: Path) -> List[str]:
    """Reads a file with UTF-8 decoding and returns a list of lines."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    except Exception:
        return []

def extract_method_range(lines: List[str], method_name: str) -> Tuple[int, int, str]:
    """
    Finds the starting line, ending line, and code snippet for a method in Java/Kotlin.
    Returns (startLine, endLine, snippet).
    """
    pattern = re.compile(rf'\b(?:public|protected|private|static|\s)+\s+[\w\<\>\[\]\,]+\s+{re.escape(method_name)}\s*\(', re.MULTILINE)
    
    for i, line in enumerate(lines):
        if pattern.search(line):
            start_line = i + 1
            # Track braces to find end line
            brace_count = 0
            found_opening = False
            end_line = start_line
            
            for j in range(i, len(lines)):
                l = lines[j]
                if '{' in l:
                    found_opening = True
                    brace_count += l.count('{')
                if '}' in l:
                    brace_count -= l.count('}')
                
                if found_opening and brace_count <= 0:
                    end_line = j + 1
                    break
            
            snippet = "".join(lines[i:end_line])
            return start_line, end_line, snippet
            
    return 1, min(len(lines), 30), "".join(lines[:min(len(lines), 30)])

def find_symbols_in_repository(repo_path: Path) -> List[InspectedSymbol]:
    """
    Discovers key architectural symbols (Controllers, Services, Repositories, Clients, Handlers).
    """
    symbols = []
    files = scan_repository_files(repo_path)
    
    for file_path in files:
        rel_path = file_path.relative_to(repo_path).as_posix()
        lines = extract_file_lines(file_path)
        content = "".join(lines)
        
        # Check class declaration
        class_match = re.search(r'\b(?:public\s+)?(?:class|interface|record)\s+(\w+)', content)
        class_name = class_match.group(1) if class_match else file_path.stem
        
        # Identify role
        role = "SERVICE"
        if "@RestController" in content or "@Controller" in content or "controller" in rel_path.lower():
            role = "CONTROLLER"
        elif "@Repository" in content or "repository" in rel_path.lower():
            role = "REPOSITORY"
        elif "@RestControllerAdvice" in content or "@ExceptionHandler" in content or "exception" in rel_path.lower():
            role = "EXCEPTION_HANDLER"
        elif "client" in rel_path.lower() or "HttpClient" in content:
            role = "CLIENT"
        elif "Test" in file_path.name or "test" in rel_path.lower():
            role = "TEST"
        elif rel_path.endswith((".yml", ".yaml")):
            role = "CONFIG"
            
        # Discover methods inside classes
        method_matches = re.finditer(r'\b(?:public|protected)\s+[\w\<\>\[\]\,]+\s+(\w+)\s*\(', content)
        found_any_method = False
        for mm in method_matches:
            found_any_method = True
            m_name = mm.group(1)
            start_l, end_l, snip = extract_method_range(lines, m_name)
            symbols.append(InspectedSymbol(
                filePath=rel_path,
                className=class_name,
                methodName=m_name,
                startLine=start_l,
                endLine=end_l,
                snippet=snip[:800],
                role=role
            ))
            
        if not found_any_method:
            symbols.append(InspectedSymbol(
                filePath=rel_path,
                className=class_name,
                methodName=None,
                startLine=1,
                endLine=min(len(lines), 40),
                snippet=content[:800],
                role=role
            ))
            
    return symbols

def search_symbol_by_name(repo_path: Path, class_or_file: str, method_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Locates a specific class/file and optional method with exact lines and source text."""
    files = scan_repository_files(repo_path)
    clean_target = class_or_file.replace(".", "/").split("/")[-1]
    
    for f in files:
        if clean_target.lower() in f.name.lower() or f.stem.lower() == clean_target.lower():
            rel_path = f.relative_to(repo_path).as_posix()
            lines = extract_file_lines(f)
            if method_name:
                start_l, end_l, snip = extract_method_range(lines, method_name)
                return {
                    "filePath": rel_path,
                    "className": f.stem,
                    "methodName": method_name,
                    "startLine": start_l,
                    "endLine": end_l,
                    "snippet": snip,
                    "fullLines": lines
                }
            else:
                return {
                    "filePath": rel_path,
                    "className": f.stem,
                    "methodName": None,
                    "startLine": 1,
                    "endLine": len(lines),
                    "snippet": "".join(lines[:50]),
                    "fullLines": lines
                }
    return None

def trace_execution_path_from_evidence(
    repo_path: Path,
    service_name: str,
    endpoint: Optional[str],
    stack_trace: str
) -> List[ExecutionPathStep]:
    """
    Builds the step-by-step code execution path:
    Request Ingress (Controller) -> Business Service -> Repository / Downstream -> Exception Handler.
    Uses real file contents to extract exact line ranges and code snippets.
    """
    steps: List[ExecutionPathStep] = []
    step_num = 1
    
    # 1. Search for Ingress Controller
    files = scan_repository_files(repo_path)
    controller_file = None
    controller_method = None
    
    for f in files:
        if "controller" in f.name.lower():
            lines = extract_file_lines(f)
            content = "".join(lines)
            if endpoint and any(part in content for part in endpoint.split("/") if len(part) > 3):
                controller_file = f
                # Look for matching Mapping method
                for i, l in enumerate(lines):
                    if "@PostMapping" in l or "@GetMapping" in l or "@RequestMapping" in l:
                        # Find the method right after
                        for k in range(i + 1, min(i + 5, len(lines))):
                            m = re.search(r'\bpublic\s+[\w\<\>\[\]\,]+\s+(\w+)\s*\(', lines[k])
                            if m:
                                controller_method = m.group(1)
                                break
                        if controller_method:
                            break
                break
                
    if controller_file:
        lines = extract_file_lines(controller_file)
        rel_path = controller_file.relative_to(repo_path).as_posix()
        m_name = controller_method or "handleRequest"
        start_l, end_l, snip = extract_method_range(lines, m_name)
        steps.append(ExecutionPathStep(
            stepNumber=step_num,
            service=service_name,
            className=controller_file.stem,
            methodName=m_name,
            filePath=rel_path,
            startLine=start_l,
            endLine=end_l,
            reason=f"Ingress HTTP routing controller bound to endpoint contract '{endpoint or '/'}'",
            evidenceType="STATICALLY_INFERRED",
            evidenceReference=f"Controller route annotation in {rel_path}:{start_l}",
            snippet=snip[:400]
        ))
        step_num += 1

    # 2. Extract Stack Trace Method Calls
    stack_pattern = re.findall(r'at\s+([\w\.\$]+)\.([\w\<]+)\(([\w\.\-]+):(\d+)\)', stack_trace)
    
    # Invert so chronological order: from outer caller down to deepest failure
    seen_methods = set()
    for class_fqn, method_name, file_name, line_str in reversed(stack_pattern):
        line_num = int(line_str)
        simple_class = class_fqn.split(".")[-1].split("$")[0]
        method_key = f"{simple_class}.{method_name}"
        if method_key in seen_methods:
            continue
        seen_methods.add(method_key)
        
        # Search repo for file
        found_info = search_symbol_by_name(repo_path, simple_class, method_name)
        if found_info:
            rel_path = found_info["filePath"]
            start_l = found_info["startLine"]
            end_l = found_info["endLine"]
            snip = found_info["snippet"]
            
            steps.append(ExecutionPathStep(
                stepNumber=step_num,
                service=service_name,
                className=simple_class,
                methodName=method_name,
                filePath=rel_path,
                startLine=min(start_l, line_num),
                endLine=max(end_l, line_num),
                reason=f"Active execution frame observed in runtime stack trace at line {line_num}",
                evidenceType="OBSERVED",
                evidenceReference=f"Server stack trace frame at {file_name}:{line_num}",
                snippet=snip[:400]
            ))
            step_num += 1

    # 3. Search for Exception Handler or Error Boundary
    for f in files:
        if "exception" in f.name.lower() or "handler" in f.name.lower():
            lines = extract_file_lines(f)
            content = "".join(lines)
            if "@ExceptionHandler" in content:
                rel_path = f.relative_to(repo_path).as_posix()
                steps.append(ExecutionPathStep(
                    stepNumber=step_num,
                    service=service_name,
                    className=f.stem,
                    methodName="handleException",
                    filePath=rel_path,
                    startLine=1,
                    endLine=min(len(lines), 35),
                    reason="Global REST exception advisor capturing uncaught runtime error and formatting HTTP response",
                    evidenceType="STATICALLY_INFERRED",
                    evidenceReference=f"@RestControllerAdvice in {rel_path}",
                    snippet=content[:400]
                ))
                step_num += 1
                break

    # If steps are empty (e.g. no stack trace in logs), provide static default path
    if not steps:
        for f in files:
            if "service" in f.name.lower() and not "test" in f.name.lower():
                lines = extract_file_lines(f)
                rel_path = f.relative_to(repo_path).as_posix()
                steps.append(ExecutionPathStep(
                    stepNumber=1,
                    service=service_name,
                    className=f.stem,
                    methodName="execute",
                    filePath=rel_path,
                    startLine=1,
                    endLine=min(len(lines), 30),
                    reason="Inferred primary service handler based on repository naming heuristics",
                    evidenceType="UNCERTAIN",
                    evidenceReference="Repository catalog module hint",
                    snippet="".join(lines[:30])
                ))
                break

    return steps

def identify_failure_locations_from_code(
    repo_path: Path,
    stack_trace: str,
    error_message: str
) -> List[FailureLocation]:
    """
    Distinguishes three distinct physical locations in the codebase:
    1. OBSERVED: Where error was caught or recorded in log.
    2. PROPAGATED: Intermediary caller / framework boundary that passed the failure upward.
    3. ROOT_CAUSE: The actual line or method causing the defect (e.g. missing lock, unhandled retry, timeout).
    """
    locations: List[FailureLocation] = []
    stack_matches = re.findall(r'at\s+([\w\.\$]+)\.([\w\<]+)\(([\w\.\-]+):(\d+)\)', stack_trace)
    
    if stack_matches:
        # First match is deepest observed failure
        deep_class, deep_method, deep_file, deep_line = stack_matches[0]
        deep_simple = deep_class.split(".")[-1].split("$")[0]
        deep_line_num = int(deep_line)
        
        found_deep = search_symbol_by_name(repo_path, deep_simple, deep_method)
        deep_snippet = found_deep["snippet"] if found_deep else f"// Line {deep_line_num} in {deep_file}"
        deep_path = found_deep["filePath"] if found_deep else f"src/main/java/{deep_class.replace('.', '/')}.java"
        
        locations.append(FailureLocation(
            category="OBSERVED",
            title=f"Exception Ingress: {deep_simple}.{deep_method}",
            description=f"Direct point where exception was thrown or reported during runtime execution: {error_message[:120]}",
            filePath=deep_path,
            className=deep_simple,
            methodName=deep_method,
            line=deep_line_num,
            snippet=deep_snippet[:500],
            evidenceReason=f"Topmost stack frame in server error log at {deep_file}:{deep_line_num}"
        ))
        
        # Second match or caller is propagation layer
        if len(stack_matches) > 1:
            caller_class, caller_method, caller_file, caller_line = stack_matches[1]
            caller_simple = caller_class.split(".")[-1].split("$")[0]
            caller_line_num = int(caller_line)
            found_caller = search_symbol_by_name(repo_path, caller_simple, caller_method)
            caller_snippet = found_caller["snippet"] if found_caller else f"// Line {caller_line_num} in {caller_file}"
            caller_path = found_caller["filePath"] if found_caller else f"src/main/java/{caller_class.replace('.', '/')}.java"
            
            locations.append(FailureLocation(
                category="PROPAGATED",
                title=f"Propagation Frame: {caller_simple}.{caller_method}",
                description=f"Calling method that invoked the failing operation without an active fallback, retry, or circuit breaker envelope.",
                filePath=caller_path,
                className=caller_simple,
                methodName=caller_method,
                line=caller_line_num,
                snippet=caller_snippet[:500],
                evidenceReason=f"Caller stack frame in server trace at {caller_file}:{caller_line_num}"
            ))
            
            # Root cause location is in the calling business logic where safeguard should be added
            locations.append(FailureLocation(
                category="ROOT_CAUSE",
                title=f"Root Cause Defect: {caller_simple}.{caller_method}",
                description=f"Underlying vulnerability or missing concurrency/timeout safeguard allowing the collision or timeout to occur.",
                filePath=caller_path,
                className=caller_simple,
                methodName=caller_method,
                line=caller_line_num,
                snippet=caller_snippet[:500],
                evidenceReason="Architectural source location requiring code fix and defensive retry or circuit breaker handling."
            ))
    
    return locations

def find_test_files_for_codebase(repo_path: Path, class_name: str) -> List[Dict[str, Any]]:
    """Discovers existing test files corresponding to the inspected class."""
    files = scan_repository_files(repo_path)
    tests = []
    clean_target = class_name.replace("Test", "")
    
    for f in files:
        if "test" in f.name.lower() or "spec" in f.name.lower():
            if clean_target.lower() in f.name.lower():
                rel_path = f.relative_to(repo_path).as_posix()
                lines = extract_file_lines(f)
                content = "".join(lines)
                tests.append({
                    "filePath": rel_path,
                    "className": f.stem,
                    "content": content[:800],
                    "linesCount": len(lines)
                })
    return tests
