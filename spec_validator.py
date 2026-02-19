"""
Spec Validator Module

Provides validation utilities for spec-driven development artifacts.
"""

import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ConstitutionValidator:
    """Validates constitution compliance."""
    
    @staticmethod
    def extract_principles(constitution: str) -> List[str]:
        """
        Extract principle names from constitution.
        
        Args:
            constitution: Constitution markdown content
            
        Returns:
            List of principle names
        """
        principles = []
        lines = constitution.split('\n')
        
        for line in lines:
            # Look for markdown headers (### or ##)
            if line.strip().startswith('###') or line.strip().startswith('##'):
                principle = line.strip().lstrip('#').strip()
                # Skip common section headers
                if principle and principle.lower() not in [
                    'core principles', 'principles', 'governance',
                    'additional constraints', 'sections'
                ]:
                    principles.append(principle)
        
        return principles
    
    @staticmethod
    def check_plan_compliance(plan: str, constitution: str) -> Dict[str, bool]:
        """
        Check if plan mentions constitution compliance.
        
        Args:
            plan: Plan markdown content
            constitution: Constitution markdown content
            
        Returns:
            Dict with compliance check results
        """
        principles = ConstitutionValidator.extract_principles(constitution)
        
        results = {
            'has_constitution_section': 'constitution check' in plan.lower(),
            'mentions_principles': False,
            'has_compliance_checklist': '- [ ]' in plan or '- [x]' in plan,
            'principle_coverage': {}
        }
        
        # Check if each principle is mentioned
        for principle in principles:
            mentioned = principle.lower() in plan.lower()
            results['principle_coverage'][principle] = mentioned
            if mentioned:
                results['mentions_principles'] = True
        
        return results


class TaskValidator:
    """Validates task list format and structure."""
    
    @staticmethod
    def validate_task_format(tasks: str) -> Dict[str, any]:
        """
        Validate task list follows proper format.
        
        Args:
            tasks: Tasks markdown content
            
        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'total_tasks': 0,
            'tasks_with_checkboxes': 0,
            'tasks_with_ids': 0,
            'tasks_with_file_paths': 0,
            'parallel_tasks': 0,
            'story_labeled_tasks': 0,
            'errors': [],
            'warnings': []
        }
        
        # Find all task lines
        task_pattern = r'^\s*-\s*\[\s*\]\s*(T\d+)?\s*(\[P\])?\s*(\[US\d+\])?\s*(.+)$'
        lines = tasks.split('\n')
        
        task_ids = set()
        
        for line_num, line in enumerate(lines, 1):
            # Check for checkbox tasks
            if re.match(r'^\s*-\s*\[', line):
                results['tasks_with_checkboxes'] += 1
                results['total_tasks'] += 1
                
                match = re.match(task_pattern, line)
                if match:
                    task_id, parallel, story, description = match.groups()
                    
                    # Validate task ID
                    if task_id:
                        results['tasks_with_ids'] += 1
                        
                        # Check for duplicate IDs
                        if task_id in task_ids:
                            results['errors'].append(
                                f"Line {line_num}: Duplicate task ID {task_id}"
                            )
                            results['valid'] = False
                        task_ids.add(task_id)
                    else:
                        results['warnings'].append(
                            f"Line {line_num}: Task missing ID"
                        )
                    
                    # Check parallel marker
                    if parallel:
                        results['parallel_tasks'] += 1
                    
                    # Check story label
                    if story:
                        results['story_labeled_tasks'] += 1
                    
                    # Check for file path in description
                    if description:
                        # Look for common path patterns
                        if '/' in description or '\\' in description or '.' in description:
                            if any(ext in description for ext in ['.py', '.js', '.ts', '.java', '.go', '.rs']):
                                results['tasks_with_file_paths'] += 1
                else:
                    results['warnings'].append(
                        f"Line {line_num}: Task doesn't match expected format"
                    )
        
        # Validate task count
        if results['total_tasks'] == 0:
            results['errors'].append("No tasks found in document")
            results['valid'] = False
        
        # Check ID coverage
        if results['tasks_with_ids'] < results['total_tasks']:
            results['warnings'].append(
                f"{results['total_tasks'] - results['tasks_with_ids']} tasks missing IDs"
            )
        
        return results
    
    @staticmethod
    def validate_phase_structure(tasks: str) -> Dict[str, any]:
        """
        Validate task organization into phases.
        
        Args:
            tasks: Tasks markdown content
            
        Returns:
            Dict with phase validation results
        """
        results = {
            'has_phases': False,
            'phases_found': [],
            'has_setup_phase': False,
            'has_foundational_phase': False,
            'has_user_story_phases': False,
            'errors': []
        }
        
        # Look for phase headers
        phase_pattern = r'^##\s+Phase\s+\d+:'
        user_story_pattern = r'User Story \d+'
        
        lines = tasks.split('\n')
        for line in lines:
            if re.match(phase_pattern, line, re.IGNORECASE):
                results['has_phases'] = True
                results['phases_found'].append(line.strip())
                
                if 'setup' in line.lower():
                    results['has_setup_phase'] = True
                elif 'foundational' in line.lower() or 'foundation' in line.lower():
                    results['has_foundational_phase'] = True
                elif re.search(user_story_pattern, line, re.IGNORECASE):
                    results['has_user_story_phases'] = True
        
        # Validate minimum structure
        if not results['has_setup_phase']:
            results['errors'].append("Missing Setup phase")
        
        if not results['has_foundational_phase']:
            results['errors'].append("Missing Foundational phase")
        
        return results
    
    @staticmethod
    def extract_dependencies(tasks: str) -> List[Tuple[str, List[str]]]:
        """
        Extract task dependencies from tasks document.
        
        Args:
            tasks: Tasks markdown content
            
        Returns:
            List of (task_id, dependencies) tuples
        """
        dependencies = []
        
        # Look for dependency section
        lines = tasks.split('\n')
        in_dependency_section = False
        
        for line in lines:
            if 'dependencies' in line.lower() and ('##' in line or '###' in line):
                in_dependency_section = True
            elif in_dependency_section:
                if line.strip().startswith('##'):
                    in_dependency_section = False
                
                # Look for dependency patterns like "T001 → T002, T003"
                dep_match = re.search(r'(T\d+)\s*[→->]\s*(.+)', line)
                if dep_match:
                    task_id = dep_match.group(1)
                    deps_str = dep_match.group(2)
                    deps = [d.strip() for d in re.findall(r'T\d+', deps_str)]
                    dependencies.append((task_id, deps))
        
        return dependencies


class PlanValidator:
    """Validates implementation plan structure."""
    
    @staticmethod
    def validate_sections(plan: str) -> Dict[str, bool]:
        """
        Check if plan contains required sections.
        
        Args:
            plan: Plan markdown content
            
        Returns:
            Dict with section presence checks
        """
        sections = {
            'summary': False,
            'technical_context': False,
            'constitution_check': False,
            'project_structure': False,
            'data_model': False,
            'implementation_phases': False
        }
        
        plan_lower = plan.lower()
        
        # Check for each section
        if 'summary' in plan_lower or '## summary' in plan_lower:
            sections['summary'] = True
        
        if 'technical context' in plan_lower or 'tech stack' in plan_lower:
            sections['technical_context'] = True
        
        if 'constitution' in plan_lower:
            sections['constitution_check'] = True
        
        if 'project structure' in plan_lower or 'directory structure' in plan_lower:
            sections['project_structure'] = True
        
        if 'data model' in plan_lower or 'entities' in plan_lower:
            sections['data_model'] = True
        
        if 'phase' in plan_lower and ('implementation' in plan_lower or 'phases' in plan_lower):
            sections['implementation_phases'] = True
        
        return sections
    
    @staticmethod
    def extract_tech_stack(plan: str) -> Dict[str, Optional[str]]:
        """
        Extract technology stack information from plan.
        
        Args:
            plan: Plan markdown content
            
        Returns:
            Dict with extracted tech stack components
        """
        tech_stack = {
            'language': None,
            'framework': None,
            'database': None,
            'architecture': None
        }
        
        # Simple extraction - look for common patterns
        lines = plan.split('\n')
        for line in lines:
            line_lower = line.lower()
            
            # Language detection
            for lang in ['python', 'javascript', 'typescript', 'java', 'go', 'rust', 'c#']:
                if lang in line_lower:
                    tech_stack['language'] = lang.title()
                    break
            
            # Framework detection
            for fw in ['fastapi', 'flask', 'django', 'express', 'react', 'vue', 'angular', 'next.js']:
                if fw in line_lower:
                    tech_stack['framework'] = fw
                    break
            
            # Database detection
            for db in ['postgresql', 'postgres', 'mysql', 'mongodb', 'redis', 'sqlite']:
                if db in line_lower:
                    tech_stack['database'] = db.title()
                    break
        
        return tech_stack


class ImplementationValidator:
    """Validates implementation output."""
    
    @staticmethod
    def validate_code_blocks(implementation: str) -> Dict[str, any]:
        """
        Validate code blocks in implementation.
        
        Args:
            implementation: Implementation markdown content
            
        Returns:
            Dict with code block validation results
        """
        results = {
            'total_code_blocks': 0,
            'blocks_with_language': 0,
            'blocks_with_file_paths': 0,
            'languages_found': set(),
            'file_paths': []
        }
        
        lines = implementation.split('\n')
        i = 0
        
        while i < len(lines):
            if lines[i].strip().startswith('```'):
                results['total_code_blocks'] += 1
                
                # Extract language
                lang = lines[i].strip()[3:].strip()
                if lang:
                    results['blocks_with_language'] += 1
                    results['languages_found'].add(lang)
                
                # Check previous lines for file path
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if 'file' in prev_line.lower() and ':' in prev_line:
                        file_path = prev_line.split(':', 1)[1].strip()
                        results['file_paths'].append(file_path)
                        results['blocks_with_file_paths'] += 1
                
                # Skip to end of code block
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
            
            i += 1
        
        results['languages_found'] = list(results['languages_found'])
        return results
    
    @staticmethod
    def check_task_coverage(implementation: str, tasks: str) -> Dict[str, any]:
        """
        Check if implementation covers all tasks.
        
        Args:
            implementation: Implementation markdown content
            tasks: Tasks markdown content
            
        Returns:
            Dict with task coverage results
        """
        # Extract task IDs from tasks
        task_ids = set(re.findall(r'\bT\d+\b', tasks))
        
        # Find which task IDs are mentioned in implementation
        mentioned_tasks = set(re.findall(r'\bT\d+\b', implementation))
        
        results = {
            'total_tasks': len(task_ids),
            'tasks_mentioned': len(mentioned_tasks),
            'coverage_percentage': (len(mentioned_tasks) / len(task_ids) * 100) if task_ids else 0,
            'missing_tasks': list(task_ids - mentioned_tasks),
            'extra_tasks': list(mentioned_tasks - task_ids)
        }
        
        return results


def validate_workflow(base_dir: Path) -> Dict[str, any]:
    """
    Comprehensive validation of entire workflow.
    
    Args:
        base_dir: Base directory containing all artifacts
        
    Returns:
        Dict with comprehensive validation results
    """
    results = {
        'constitution': None,
        'spec': None,
        'plan': None,
        'tasks': None,
        'implementation': None,
        'overall_valid': True
    }
    
    # Validate constitution
    const_path = base_dir / 'constitution.md'
    if const_path.exists():
        constitution = const_path.read_text(encoding='utf-8')
        principles = ConstitutionValidator.extract_principles(constitution)
        results['constitution'] = {
            'exists': True,
            'principles_count': len(principles),
            'principles': principles
        }
    else:
        results['constitution'] = {'exists': False}
        results['overall_valid'] = False
    
    # Validate spec
    spec_path = base_dir / 'spec.md'
    if spec_path.exists():
        results['spec'] = {'exists': True}
    else:
        results['spec'] = {'exists': False}
        results['overall_valid'] = False
    
    # Validate plan
    plan_path = base_dir / 'outputs' / 'plan.md'
    if plan_path.exists():
        plan = plan_path.read_text(encoding='utf-8')
        results['plan'] = {
            'exists': True,
            'sections': PlanValidator.validate_sections(plan),
            'tech_stack': PlanValidator.extract_tech_stack(plan)
        }
        
        if constitution:
            results['plan']['constitution_compliance'] = ConstitutionValidator.check_plan_compliance(
                plan, constitution
            )
    else:
        results['plan'] = {'exists': False}
    
    # Validate tasks
    tasks_path = base_dir / 'outputs' / 'tasks.md'
    if tasks_path.exists():
        tasks = tasks_path.read_text(encoding='utf-8')
        results['tasks'] = {
            'exists': True,
            'format': TaskValidator.validate_task_format(tasks),
            'phases': TaskValidator.validate_phase_structure(tasks)
        }
        
        if not results['tasks']['format']['valid']:
            results['overall_valid'] = False
    else:
        results['tasks'] = {'exists': False}
    
    # Validate implementation
    impl_path = base_dir / 'outputs' / 'implementation.md'
    if impl_path.exists():
        implementation = impl_path.read_text(encoding='utf-8')
        results['implementation'] = {
            'exists': True,
            'code_blocks': ImplementationValidator.validate_code_blocks(implementation)
        }
        
        if tasks_path.exists():
            results['implementation']['task_coverage'] = ImplementationValidator.check_task_coverage(
                implementation, tasks
            )
    else:
        results['implementation'] = {'exists': False}
    
    return results
