"""
依赖关系解析模块

处理任务之间的依赖关系和排序
"""

from typing import Dict, List, Any


class DependencyResolver:
    """依赖关系解析器"""
    
    def topological_sort(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """拓扑排序任务依赖"""
        # 构建依赖图
        task_map = {task["id"]: task for task in tasks}
        in_degree = {task["id"]: 0 for task in tasks}
        
        # 计算入度
        for task in tasks:
            for dep in task.get("dependencies", []):
                if dep in in_degree:
                    in_degree[task["id"]] += 1
        
        # 拓扑排序
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        sorted_tasks = []
        
        while queue:
            current_id = queue.pop(0)
            current_task = task_map[current_id]
            sorted_tasks.append(current_task)
            
            # 更新依赖任务的入度
            for task in tasks:
                if current_id in task.get("dependencies", []):
                    in_degree[task["id"]] -= 1
                    if in_degree[task["id"]] == 0:
                        queue.append(task["id"])
        
        return sorted_tasks
    
    def detect_circular_dependencies(self, tasks: List[Dict[str, Any]]) -> List[List[str]]:
        """检测循环依赖"""
        task_ids = {task["id"] for task in tasks}
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(task_id: str, path: List[str]) -> bool:
            if task_id in rec_stack:
                # 找到循环
                cycle_start = path.index(task_id)
                cycles.append(path[cycle_start:] + [task_id])
                return True
            
            if task_id in visited:
                return False
            
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task:
                for dep in task.get("dependencies", []):
                    if dep in task_ids:
                        if dfs(dep, path + [task_id]):
                            return True
            
            rec_stack.remove(task_id)
            return False
        
        for task in tasks:
            if task["id"] not in visited:
                dfs(task["id"], [])
        
        return cycles
    
    def validate_dependencies(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证依赖关系的有效性"""
        task_ids = {task["id"] for task in tasks}
        validation_result = {
            "valid": True,
            "missing_dependencies": [],
            "circular_dependencies": [],
            "warnings": []
        }
        
        # 检查缺失的依赖
        for task in tasks:
            for dep in task.get("dependencies", []):
                if dep not in task_ids:
                    validation_result["missing_dependencies"].append({
                        "task": task["id"], 
                        "missing_dep": dep
                    })
                    validation_result["valid"] = False
        
        # 检查循环依赖
        cycles = self.detect_circular_dependencies(tasks)
        if cycles:
            validation_result["circular_dependencies"] = cycles
            validation_result["valid"] = False
        
        return validation_result
