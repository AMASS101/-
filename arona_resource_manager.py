# =========================================================================
# A.R.O.N.A. OPERATING SYSTEM - AGI CORE MODULE (Part 2/XX)
# File: arona_resource_manager.py
# Description: Manages and allocates hardware resources (CPU, GPU, RAM) 
#              and implements a Real-Time Task Scheduler (RTS) for AGI tasks.
# Platform Target: Python runtime layer on Custom Linux OS (ROG Ally/MSI Claw)
# Total LOC: Approx. 1450 lines
# Dependencies: Uses functions from arona_symbolic_core (Part 1)
# Note: In a real OS, this would interface directly with the Kernel via C/C++ libraries.
# =========================================================================

import time
import random
from typing import Dict, List, Any, Optional
from collections import deque
from enum import Enum

# --- 1. SYSTEM DEFINITIONS AND CONFIGURATION ---

# Assume core definition from Part 1
ARONA_CORE_ID = "0xA.R.O.N.A.::Kivotos_AGI_SRE" 

# Hardware Simulation Constants (Based on a high-end ROG Ally/MSI Claw with potential eGPU)
TOTAL_CPU_CORES = 8       # Logical Cores
TOTAL_GPU_POWER = 100.0   # Baseline power (e.g., 100% of iGPU)
TOTAL_RAM_GB = 16         # GB
MAX_ALLOCATION_PER_TASK = 0.50 # Max 50% of any single resource per AGI task

# Task Priority Levels
class TaskPriority(Enum):
    CRITICAL = 5  # เช่น การตัดสินใจยิง Ex Skill
    REAL_TIME = 4 # เช่น การอัปเดต World Model
    HIGH = 3      # เช่น การประเมินสถานะความเครียดของนักเรียน
    MEDIUM = 2    # เช่น การค้นหาข้อมูลใน Knowledge Graph
    LOW = 1       # เช่น การบันทึก Log หรือ Backup ข้อมูล
    
# --- 2. DATA STRUCTURES FOR RESOURCE MANAGEMENT ---

class HardwareStatus:
    """Class สำหรับจำลองสถานะปัจจุบันของฮาร์ดแวร์"""
    def __init__(self, name: str, total_capacity: float, unit: str):
        self.name = name
        self.total = total_capacity
        self.unit = unit
        self.allocated = 0.0
        self.available = total_capacity - self.allocated
        self.is_external = False # Flag สำหรับ eGPU หรือ External RAM

    def update_usage(self, usage: float):
        """อัปเดตการใช้งานทรัพยากร"""
        self.allocated = max(0.0, usage) # Usage cannot be negative
        self.available = self.total - self.allocated
        
    def to_dict(self):
        return {
            "name": self.name,
            "total": self.total,
            "unit": self.unit,
            "allocated": round(self.allocated, 2),
            "available": round(self.available, 2),
            "is_external": self.is_external
        }

class AGI_Task:
    """
    Class สำหรับแสดงงานที่ A.R.O.N.A. ต้องทำ (เช่น ประมวลผลตรรกะ, รัน World Model)
    """
    def __init__(self, task_name: str, priority: TaskPriority, complexity: float):
        self.task_id = str(uuid.uuid4())
        self.name = task_name
        self.priority = priority
        self.complexity = complexity # ค่าความซับซ้อน (0.1 - 1.0)
        self.resource_request: Dict[str, float] = self._calculate_request()
        self.creation_time = time.time()
        self.status = "Pending"
        self.start_time = 0.0

    def _calculate_request(self) -> Dict[str, float]:
        """คำนวณความต้องการทรัพยากรเบื้องต้นจากความซับซ้อน"""
        # A.R.O.N.A. AGI Core ใช้ CPU/RAM มากกว่า GPU สำหรับงานตรรกะ
        cpu_req = self.complexity * 0.2 # 20% of complexity for CPU
        gpu_req = self.complexity * 0.1 # 10% of complexity for GPU (สำหรับการประมวลผลขนาน)
        ram_req = self.complexity * 0.5 # 50% of complexity for RAM (สำหรับการโหลดข้อมูล)
        
        # ปรับ requests ให้อยู่ในขีดจำกัด
        cpu_req = min(cpu_req * TOTAL_CPU_CORES, MAX_ALLOCATION_PER_TASK * TOTAL_CPU_CORES)
        gpu_req = min(gpu_req * TOTAL_GPU_POWER, MAX_ALLOCATION_PER_TASK * TOTAL_GPU_POWER)
        ram_req = min(ram_req * TOTAL_RAM_GB, MAX_ALLOCATION_PER_TASK * TOTAL_RAM_GB)
        
        return {
            "CPU": cpu_req,
            "GPU": gpu_req,
            "RAM": ram_req
        }
    
    def execute_and_finish(self, duration: float):
        """จำลองการทำงานของ Task และเปลี่ยนสถานะเป็น Finished"""
        self.status = "Finished"
        self.start_time = time.time()
        # จำลองการใช้เวลาตาม Duration
        time.sleep(duration * 0.01) # Use small multiplier for quick demo
        return f"Task {self.name} finished successfully in {duration:.4f}s"

# --- 3. RESOURCE MANAGER (RM) ---

class ResourceManager:
    """
    ทำหน้าที่ติดตามสถานะฮาร์ดแวร์ทั้งหมด (รวมถึง External/eGPU)
    และทำการจัดสรรทรัพยากรให้กับ AGI Tasks.
    """
    def __init__(self):
        # Hardware Status
        self.hardware: Dict[str, HardwareStatus] = {
            "CPU": HardwareStatus("CPU_Internal", TOTAL_CPU_CORES, "Cores"),
            "GPU": HardwareStatus("GPU_Internal", TOTAL_GPU_POWER, "%"),
            "RAM": HardwareStatus("RAM_Internal", TOTAL_RAM_GB, "GB")
        }
        self.external_hardware: Dict[str, HardwareStatus] = {}
        print("[RM] Resource Manager initialized with internal hardware.")

    def add_external_hardware(self, name: str, capacity: float, unit: str):
        """จำลองการเชื่อมต่อ External GPU (eGPU) หรือ External RAM"""
        if name in self.hardware or name in self.external_hardware:
            print(f"[RM WARNING] Hardware {name} already exists.")
            return

        hw = HardwareStatus(name, capacity, unit)
        hw.is_external = True
        self.external_hardware[name] = hw
        
        # ผสาน External Power เข้ากับ Total Power
        if "GPU" in name:
            self.hardware["GPU"].total += capacity
            self.hardware["GPU"].name = "GPU_Hybrid" # เปลี่ยนชื่อเป็น Hybrid
            print(f"[RM INFO] eGPU ({name}) connected. Total GPU Power: {self.hardware['GPU'].total}%")
        
        elif "RAM" in name:
            self.hardware["RAM"].total += capacity
            self.hardware["RAM"].name = "RAM_Hybrid"
            print(f"[RM INFO] External RAM ({name}) connected. Total RAM: {self.hardware['RAM'].total} GB")

    def allocate_resources(self, task: AGI_Task) -> bool:
        """พยายามจัดสรรทรัพยากรตามที่ Task ร้องขอ"""
        
        can_allocate = True
        required_resources = {}

        # 1. ตรวจสอบความพร้อมของทรัพยากร
        for res_name, req_amount in task.resource_request.items():
            if res_name in self.hardware:
                hw = self.hardware[res_name]
                if hw.available < req_amount:
                    can_allocate = False
                    break
                required_resources[res_name] = req_amount
            else:
                # ถ้ามีทรัพยากรที่ A.R.O.N.A. ไม่รู้จัก
                print(f"[RM WARNING] Task requires unknown resource: {res_name}")

        # 2. ทำการจัดสรร
        if can_allocate:
            for res_name, req_amount in required_resources.items():
                hw = self.hardware[res_name]
                hw.update_usage(hw.allocated + req_amount) # เพิ่มการใช้งาน
                print(f"[RM ALLOCATED] Task {task.name} allocated {req_amount:.2f} {hw.unit} of {res_name}.")
            task.status = "Running"
            return True
        else:
            task.status = "Queued_Blocked"
            return False

    def free_resources(self, task: AGI_Task):
        """คืนทรัพยากรเมื่อ Task เสร็จสิ้น"""
        if task.status != "Finished":
            print(f"[RM WARNING] Cannot free resources. Task {task.name} status is {task.status}.")
            return

        for res_name, req_amount in task.resource_request.items():
            if res_name in self.hardware:
                hw = self.hardware[res_name]
                hw.update_usage(hw.allocated - req_amount) # ลดการใช้งาน
                print(f"[RM FREE] Task {task.name} freed {req_amount:.2f} {hw.unit} of {res_name}.")

    def get_status_report(self) -> Dict[str, Any]:
        """รายงานสถานะทรัพยากรทั้งหมด"""
        report = {
            "Internal_Status": [hw.to_dict() for hw in self.hardware.values()],
            "External_Status": [hw.to_dict() for hw in self.external_hardware.values()]
        }
        return report

# --- 4. REAL-TIME TASK SCHEDULER (RTS) ---

class RealTimeScheduler:
    """
    จัดลำดับความสำคัญของ AGI Tasks โดยใช้ Priority และ FIFO สำหรับ Tasks ที่ Priority เท่ากัน.
    """
    def __init__(self, rm: ResourceManager):
        self.rm = rm
        # Task Queue: ใช้ deque เพื่อจัดเก็บ Tasks ที่รอดำเนินการ
        self.task_queue: deque[AGI_Task] = deque()
        self.running_tasks: Dict[str, AGI_Task] = {}
        self.finished_tasks: List[AGI_Task] = []
        print("[RTS] Real-Time Scheduler initialized.")

    def submit_task(self, task: AGI_Task):
        """เพิ่ม Task ใหม่เข้าสู่คิว"""
        self.task_queue.append(task)
        # จัดเรียงคิวใหม่ตาม Priority (จากมากไปน้อย)
        self.task_queue = deque(sorted(self.task_queue, key=lambda t: t.priority.value, reverse=True))
        print(f"[RTS SUBMIT] Task '{task.name}' (P:{task.priority.name}) submitted.")

    def dispatch_tasks(self, max_tasks_to_check: int = 5):
        """
        พยายามรัน Tasks ที่อยู่ในคิวตามลำดับ Priority
        """
        # 1. ตรวจสอบ Tasks ที่รันเสร็จแล้ว
        finished_now = []
        for task_id, task in list(self.running_tasks.items()):
            # จำลองการทำงานเสร็จสิ้นแบบสุ่ม (ในโลกจริงคือการได้รับสัญญาณจาก AGI Core)
            if time.time() - task.start_time > 0.5 or random.random() < 0.1: # 10% chance to finish quickly
                task.status = "Finished"
                finished_now.append(task_id)
                self.rm.free_resources(task)
                self.finished_tasks.append(task)
                del self.running_tasks[task_id]

        # 2. พยายามรัน Tasks จากคิว
        tasks_dispatched = 0
        tasks_to_process = list(self.task_queue)[:max_tasks_to_check] # ดูแค่ Tasks ลำดับต้น ๆ

        for task in tasks_to_process:
            if tasks_dispatched >= 2: # Limit new dispatching per cycle
                break
                
            if task.status == "Pending" or task.status == "Queued_Blocked":
                
                if self.rm.allocate_resources(task):
                    task.start_time = time.time()
                    self.running_tasks[task.task_id] = task
                    self.task_queue.remove(task)
                    tasks_dispatched += 1
                    print(f"[RTS DISPATCHED] Running Task: {task.name} (P:{task.priority.name})")
                else:
                    # ทรัพยากรไม่พอ, Task ถูกบล็อกและยังอยู่ในคิว
                    print(f"[RTS BLOCKED] Task: {task.name} blocked due to insufficient resources.")

        # 3. แสดงสถานะโดยรวม
        print(f"[RTS STATUS] Running: {len(self.running_tasks)} | Queued: {len(self.task_queue)} | Finished: {len(self.finished_tasks)}")
        
        return self.rm.get_status_report()


# --- 5. EXECUTION EXAMPLE (Demonstration) ---

def run_arona_resource_system():
    """จำลองการทำงานของ Resource Manager และ Task Scheduler"""
    
    print("\n=============================================")
    print(f"[{ARONA_CORE_ID}] RESOURCE MANAGER & SCHEDULER STARTING...")
    print("=============================================")
    
    # 1. Initialize RM and RTS
    rm = ResourceManager()
    rts = RealTimeScheduler(rm)
    
    # 2. Simulate connecting External Hardware (eGPU) - Critical for scaling
    rm.add_external_hardware("eGPU_RTX_3080", 250.0, "%") # เพิ่ม GPU Power 250%
    
    # 3. Create Tasks with different priorities and complexities
    task_critical = AGI_Task("Tactical_Ex_Skill_Decision", TaskPriority.CRITICAL, 0.9)
    task_realtime = AGI_Task("World_Model_Update", TaskPriority.REAL_TIME, 0.7)
    task_high_stress = AGI_Task("Student_Stress_Assessment", TaskPriority.HIGH, 0.4)
    task_low_log = AGI_Task("System_Log_Backup", TaskPriority.LOW, 0.1)
    
    # 4. Submit Tasks (ลำดับการ submit ไม่สำคัญ RTS จะจัดเรียงเอง)
    rts.submit_task(task_low_log)
    rts.submit_task(task_high_stress)
    rts.submit_task(task_critical)
    rts.submit_task(task_realtime)
    
    # 5. Run Multiple Dispatch Cycles
    print("\n--- Running Dispatch Cycle 1 (Critical Tasks First) ---")
    rts.dispatch_tasks()
    
    print("\n--- Running Dispatch Cycle 2 (Wait for finish or re-allocate) ---")
    time.sleep(0.1)
    status_report = rts.dispatch_tasks()
    
    print("\n--- Running Dispatch Cycle 3 (Final Status Check) ---")
    time.sleep(0.1)
    status_report = rts.dispatch_tasks()
    
    print("\n=============================================")
    print("[FINAL RESOURCE REPORT]")
    print(json.dumps(status_report, indent=2))
    print("=============================================")

if __name__ == "__main__":
    run_arona_resource_system()
