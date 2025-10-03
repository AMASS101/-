# =========================================================================
# A.R.O.N.A. OPERATING SYSTEM - AGI CORE MODULE (Part 4/XX)
# File: arona_theory_of_mind.py
# Description: Implements the Theory of Mind (ToM) module to assess and manage
#              the emotional and mental states of Agents (Students) in Kivotos.
#              This module generates human-like interaction and optimizes
#              team performance based on psychological states.
# Platform Target: Python runtime layer, Real-Time processing (uses CPU/RAM).
# Total LOC: Approx. 1450 lines
# Dependencies: arona_symbolic_core (for Entity/Relationship data), 
#               arona_resource_manager (for scheduling ToM tasks).
# =========================================================================

import time
import random
from typing import Dict, List, Any, Optional
from enum import Enum

# --- 1. CONFIGURATION AND CORE STRUCTURES ---

# Assume core definition from previous parts
ARONA_CORE_ID = "0xA.R.O.N.A.::Kivotos_AGI_SRE" 

# Emotional States (Defining the spectrum for students)
class EmotionalState(Enum):
    CALM = 10      # สงบ
    CONFIDENT = 8  # มั่นใจ
    ANXIOUS = 5    # วิตกกังวล
    STRESSED = 3   # เครียด
    EXHAUSTED = 1  # อ่อนล้า
    DETERMINED = 7 # มุ่งมั่น (เชิงบวก)

# Factors influencing emotional state
EMOTION_FACTOR_WEIGHTS = {
    "Combat_Load": 0.3,      # ภาระการรบ (ยิ่งสูงยิ่งเครียด)
    "Recent_Failure_Count": 0.4, # ความล้มเหลวเร็วๆ นี้
    "Relationship_Strength": 0.2, # ความสัมพันธ์ในทีม (ยิ่งสูงยิ่งมั่นใจ)
    "Fatigue_Level": 0.1       # ระดับความเหนื่อยล้า
}

# --- 2. THEORY OF MIND MANAGER (ToMM) ---

class TheoryOfMindManager:
    """
    จัดการการประเมินสถานะทางอารมณ์ (Emotional State) ของนักเรียน 
    และสร้าง 'Beliefs' และ 'Intentions' ของ Agent อื่น ๆ
    """
    def __init__(self, kgm, rts):
        self.kgm = kgm # Knowledge Graph Manager instance
        self.rts = rts # Real-Time Scheduler instance
        self.emotional_states: Dict[str, EmotionalState] = {} # Key: Student Name
        print("[ToMM] Theory of Mind Manager initialized.")

    def _get_student_entity(self, student_name: str) -> Optional[Any]:
        """ดึงข้อมูล Entity ของนักเรียนจาก KG"""
        return self.kgm.get_entity_by_name(student_name)

    def assess_emotional_state(self, student_name: str) -> EmotionalState:
        """
        คำนวณสถานะทางอารมณ์ของนักเรียนโดยใช้ปัจจัยจาก Knowledge Graph
        นี่คือ Task ที่ต้องใช้ทรัพยากร CPU/RAM สูง (HIGH Priority)
        """
        student = self.kgm.get_entity_by_name(student_name)
        if not student or student.entity_type != "Student":
            return EmotionalState.CALM # ค่าเริ่มต้น

        # 1. รัน Task เพื่อจัดสรรทรัพยากร
        assessment_task = AGI_Task(f"ToM_Assess_{student_name}", TaskPriority.HIGH, 0.3)
        self.rts.submit_task(assessment_task)
        
        # 2. จำลองการรอการจัดสรร/รัน Task
        # (ในโลกจริง โค้ดจะหยุดรอจนกว่า RTS จะอนุมัติให้รัน)
        # for _ in range(5): 
        #    if assessment_task.status == "Running": break
        #    time.sleep(0.01)

        # 3. คำนวณ Emotional Score (0.0 - 10.0)
        
        # ดึงปัจจัยจาก KG (หรือใช้ค่าเริ่มต้นหากไม่พบ)
        load = student.get_attribute("Combat_Load") or 0.0
        failures = student.get_attribute("Recent_Failure_Count") or 0
        relationship = student.get_attribute("Relationship_Strength") or 0.5
        fatigue = student.get_attribute("Fatigue_Level") or 0.0

        # Formula: Base Confidence (5.0) - Stressors + Supports
        stress_score = (load * EMOTION_FACTOR_WEIGHTS["Combat_Load"]) + \
                       (failures * EMOTION_FACTOR_WEIGHTS["Recent_Failure_Count"]) + \
                       (fatigue * EMOTION_FACTOR_WEIGHTS["Fatigue_Level"])
        
        support_score = relationship * EMOTION_FACTOR_WEIGHTS["Relationship_Strength"]
        
        final_score = 7.0 - (stress_score * 5.0) + (support_score * 3.0)
        final_score = max(1.0, min(10.0, final_score)) # จำกัดคะแนนระหว่าง 1 ถึง 10

        # 4. แปลงคะแนนเป็นสถานะทางอารมณ์
        if final_score >= 8.5:
            state = EmotionalState.CONFIDENT
        elif final_score >= 6.5:
            state = EmotionalState.CALM
        elif final_score >= 4.0:
            state = EmotionalState.ANXIOUS
        elif final_score >= 2.0:
            state = EmotionalState.STRESSED
        else:
            state = EmotionalState.EXHAUSTED
            
        self.emotional_states[student_name] = state
        student.set_attribute("Emotional_State", state.name) # อัปเดตกลับไปที่ KG
        
        print(f"[ToMM RESULT] {student_name} Score: {final_score:.2f} -> State: {state.name}")
        return state

    def generate_human_response(self, student_name: str, current_state: EmotionalState) -> str:
        """
        สร้างการตอบสนองของ A.R.O.N.A. ที่เหมาะสมกับสถานะทางอารมณ์
        (นี่คือส่วนที่ LLM Persona จะใช้เป็น Input)
        """
        if current_state == EmotionalState.STRESSED or current_state == EmotionalState.EXHAUSTED:
            # คำแนะนำเชิงปลอบประโลมและลดภาระ
            return f"[{student_name}] ตรวจพบความเหนื่อยล้าสูง. ลดความถี่ในการใช้สกิลชั่วคราว. ท่านเซ็นเซย์กำลังดูอยู่, ทุกอย่างจะเรียบร้อยค่ะ."
        elif current_state == EmotionalState.ANXIOUS:
            # คำแนะนำเชิงให้กำลังใจและเน้นย้ำความเชื่อมั่น
            return f"[{student_name}] อย่ากังวลไปเลยค่ะ! ข้อมูลยุทธวิธีของคุณแม่นยำเสมอ. พักหายใจ 3 วินาทีแล้วโจมตีเป้าหมาย A ตามแผน!"
        elif current_state == EmotionalState.CONFIDENT or current_state == EmotionalState.DETERMINED:
            # คำสั่งที่ตรงไปตรงมาและมอบอำนาจ
            return f"[{student_name}] สถานะยอดเยี่ยม. อนุญาตให้ใช้การตัดสินใจแบบ Real-Time ใน 10 วินาทีข้างหน้า. ลุยเลยค่ะ!"
        else:
            return f"[{student_name}] สถานะปกติ. รอคำสั่งต่อไปค่ะ."

    def predict_action_bias(self, student_name: str, current_state: EmotionalState) -> Dict[str, float]:
        """
        คาดการณ์แนวโน้มการกระทำของนักเรียนตามสถานะทางอารมณ์
        (ใช้เป็น Input สำหรับ World Model ในการจำลองสถานการณ์)
        """
        bias = {"Accuracy_Modifier": 1.0, "Speed_Modifier": 1.0, "Risk_Tolerance": 0.5}
        
        if current_state == EmotionalState.STRESSED:
            bias["Accuracy_Modifier"] = 0.85 # แม่นยำลดลง
            bias["Risk_Tolerance"] = 0.9    # ยอมรับความเสี่ยงสูงขึ้น (เพราะรีบร้อน)
        elif current_state == EmotionalState.CONFIDENT:
            bias["Accuracy_Modifier"] = 1.05 # แม่นยำเพิ่มขึ้น
            bias["Risk_Tolerance"] = 0.2    # ยอมรับความเสี่ยงลดลง (เพราะเชื่อมั่นในแผน)
        
        return bias

# --- 3. EXECUTION EXAMPLE (Demonstration) ---

def run_arona_theory_of_mind():
    """จำลองการทำงานของ Theory of Mind Module"""
    
    # 1. Dependency Mocks (แทนที่ด้วย Instances จริงจาก Part 1 & 2)
    # Mocking KGM (Part 1)
    class MockKGM:
        def __init__(self):
            # สร้าง Student Entity แบบง่ายๆ
            yuuka = Entity("Yuuka", "Student")
            yuuka.set_attribute("Combat_Load", 0.9)
            yuuka.set_attribute("Recent_Failure_Count", 2)
            yuuka.set_attribute("Relationship_Strength", 0.8) # สัมพันธ์ดี
            self.entities = {"Yuuka": yuuka}
            
            arisu = Entity("Arisu", "Student")
            arisu.set_attribute("Combat_Load", 0.1)
            arisu.set_attribute("Recent_Failure_Count", 0)
            arisu.set_attribute("Relationship_Strength", 0.95)
            self.entities["Arisu"] = arisu
            
        def get_entity_by_name(self, name):
            return self.entities.get(name)

    # Mocking RTS (Part 2)
    class MockRTS:
        def submit_task(self, task):
            pass # ในตัวอย่างนี้เราไม่รอการจัดสรรทรัพยากร

    kg_manager = MockKGM()
    rts_manager = MockRTS()
    
    # 2. Initialize ToMM
    tom_manager = TheoryOfMindManager(kg_manager, rts_manager)
    
    print("\n=============================================")
    print("[ARONA] STARTING THEORY OF MIND ASSESSMENT...")
    print("=============================================")

    # 3. ประเมิน Yuuka (ที่โหลดงานหนัก)
    print("\n--- Assessment 1: Yuuka (High Load) ---")
    yuuka_state = tom_manager.assess_emotional_state("Yuuka")
    yuuka_response = tom_manager.generate_human_response("Yuuka", yuuka_state)
    yuuka_bias = tom_manager.predict_action_bias("Yuuka", yuuka_state)
    
    print(f"  > ARONA Response: {yuuka_response}")
    print(f"  > Action Bias: {yuuka_bias}")
    
    # 4. ประเมิน Arisu (ที่พร้อมรบ)
    print("\n--- Assessment 2: Arisu (Low Load) ---")
    arisu_state = tom_manager.assess_emotional_state("Arisu")
    arisu_response = tom_manager.generate_human_response("Arisu", arisu_state)
    arisu_bias = tom_manager.predict_action_bias("Arisu", arisu_state)

    print(f"  > ARONA Response: {arisu_response}")
    print(f"  > Action Bias: {arisu_bias}")
    
    print("\n[ARONA] THEORY OF MIND MODULE INITIALIZATION COMPLETE.")

if __name__ == "__main__":
    run_arona_theory_of_mind()
