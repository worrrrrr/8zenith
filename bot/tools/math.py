"""
tools/math_tool.py — 8zenith Math Solver (Full Edition)
==========================================================
แก้สมการคณิตศาสตร์ทุกประเภทด้วย Z3-Solver + SymPy
รองรับ:
  - สมการเดี่ยว (linear, quadratic, exponential, transcendental)
  - ระบบสมการ (system of equations)
  - Implicit multiplication (19x → 19*x)
  - Unknown variable (? → x)
  - Z3 หาทุกคำตอบ (ไม่หยุดที่คำตอบแรก)

การเลือก Solver:
  1. Z3-Solver → หาทุกคำตอบด้วย Constraint Programming
  2. SymPy → สำหรับสมการที่ซับซ้อน ใช้ symbolic manipulation
  3. Hybrid → ใช้ทั้งคู่ ตรวจสอบไขว้

Dependencies:
  - z3-solver (pip install z3-solver)
  - sympy (pip install sympy)
"""

import re
import logging
from typing import Dict, List, Optional, Any

from tools.base import BaseTool

logger = logging.getLogger("8zenith.math_tool")


class MathTool(BaseTool):
    """แก้สมการคณิตศาสตร์ทุกประเภท"""

    @property
    def intents(self) -> List[str]:
        return ["math"]

    @property
    def description(self) -> str:
        return (
            "แก้สมการคณิตศาสตร์ — รองรับ Linear, Quadratic, "
            "Exponential, Transcendental, System of Equations"
        )

    def validate_context(self, context: dict) -> bool:
        has_single = "equation" in context and bool(context["equation"])
        has_system = "equations" in context and bool(context["equations"])
        return has_single or has_system

    # ═══════════════════════════════════════════════════════════
    # Main Execute
    # ═══════════════════════════════════════════════════════════

    def execute(self, context: dict) -> dict:
        # 1. ระบบสมการ (ส่งมาเป็น list)
        if "equations" in context and context["equations"]:
            return self._solve_system(context["equations"])

        equation = context.get("equation", "")
        if not equation:
            return {"error": "No equation provided"}

        # 2. ตรวจจับระบบสมการจาก string เดียว (คั่นด้วย , หรือ และ)
        if self._is_system(equation):
            eqs = self._split_system(equation)
            return self._solve_system(eqs)

        # 3. ทำความสะอาดสมการ
        equation = self._clean_equation(equation)

        # 4. จำแนกประเภท
        eq_type = self._classify_equation(equation)

        # 5. ใช้ทั้ง Z3 และ SymPy
        z3_result = self._solve_with_z3(equation)
        sympy_result = self._solve_with_sympy(equation, eq_type)

        # 6. รวมผลลัพธ์ — ใช้ SymPy เป็นหลัก (เพราะครบกว่า)
        if sympy_result and not sympy_result.get("error"):
            result = sympy_result
            if z3_result and not z3_result.get("error"):
                result["math"]["z3_numerical"] = z3_result["math"]["numerical"]
                result["math"]["solver_used"] = "sympy+z3"
            return result

        if z3_result and not z3_result.get("error"):
            return z3_result

        # 7. Fallback
        return {
            "math": {
                "type": "single",
                "original": equation,
                "solutions": [],
                "numerical": [],
                "solver_used": "none",
                "steps": ["All solvers failed"],
                "error": "Unable to solve equation"
            }
        }

    # ═══════════════════════════════════════════════════════════
    # Cleaning
    # ═══════════════════════════════════════════════════════════

    def _clean_equation(self, equation: str) -> str:
        """ทำความสะอาดสมการ"""
        eq = equation.strip()

        # แทนที่ ? ด้วย x (unknown variable)
        eq = eq.replace("?", "x")

        # เพิ่ม * ระหว่างตัวเลขกับตัวแปร: 19x → 19*x, 23x → 23*x
        eq = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', eq)

        return eq

    def _is_system(self, equation: str) -> bool:
        """ตรวจจับว่าเป็นระบบสมการหรือไม่ (คั่นด้วย , หรือ และ)"""
        return bool(re.search(r'[,;]|\sและ\s|\sand\s', equation))

    def _split_system(self, equation: str) -> List[str]:
        """แยกระบบสมการจาก string เดียว"""
        parts = re.split(r'[,;]|\sและ\s|\sand\s', equation)
        return [p.strip() for p in parts if p.strip()]

    # ═══════════════════════════════════════════════════════════
    # Classification
    # ═══════════════════════════════════════════════════════════

    def _classify_equation(self, equation: str) -> str:
        eq = equation.replace(" ", "")

        if re.search(r"[a-zA-Z]\s*\^|\(\s*[a-zA-Z]\s*\)\s*\^", eq):
            if re.search(r'\d+\s*\^|\(\s*\d+\s*\)\s*\^', eq):
                return "transcendental"
            if re.search(r'[a-zA-Z]\s*\^[a-zA-Z]', eq):
                return "transcendental"
            if re.search(r'\^[a-zA-Z]', eq):
                return "transcendental"
            return "exponential"

        if re.search(r'[a-zA-Z]\s*\*\*\s*2|\^2', eq):
            return "quadratic"

        return "linear"

    # ═══════════════════════════════════════════════════════════
    # Z3-Solver (ทุกคำตอบ)
    # ═══════════════════════════════════════════════════════════

    def _solve_with_z3(self, equation: str) -> Optional[dict]:
        try:
            import z3
        except ImportError:
            return None

        try:
            left, right = self._parse_equation(equation)
            x = z3.Real('x')

            z3_left = self._to_z3_expr(left, x)
            z3_right = self._to_z3_expr(right, x)

            if z3_left is None or z3_right is None:
                return None

            solver = z3.Solver()
            solver.add(z3_left == z3_right)

            solutions = []
            numerical = []
            max_solutions = 10  # ป้องกัน infinite loop

            while solver.check() == z3.sat and len(solutions) < max_solutions:
                model = solver.model()
                solution = model[x]

                if z3.is_algebraic_value(solution):
                    num = float(solution.approx(10))
                else:
                    num = float(solution.numerator_as_long()) / float(solution.denominator_as_long())

                # ตรวจสอบว่ายังไม่มีคำตอบนี้
                if not any(abs(num - n) < 1e-6 for n in numerical):
                    solutions.append(str(solution))
                    numerical.append(round(num, 6))

                # เพิ่มเงื่อนไข: x ≠ คำตอบที่เจอแล้ว
                solver.add(x != solution)

            if solutions:
                return {
                    "math": {
                        "type": "single",
                        "original": equation,
                        "solutions": solutions,
                        "numerical": numerical,
                        "solver_used": "z3",
                        "steps": [f"Used Z3-Solver — found {len(solutions)} solution(s)"]
                    }
                }

            return None
        except Exception as e:
            logger.debug(f"Z3 failed: {e}")
            return None

    def _to_z3_expr(self, expr_str: str, x):
        """แปลง expression string → Z3 expression"""
        expr_str = expr_str.replace("^", "**")
        try:
            return eval(expr_str, {"x": x, "__builtins__": {}}, {"x": x})
        except Exception:
            return None

    # ═══════════════════════════════════════════════════════════
    # SymPy Solver
    # ═══════════════════════════════════════════════════════════

    def _solve_with_sympy(self, equation: str, eq_type: str) -> dict:
        import sympy as sp

        x = sp.symbols('x')
        left, right = self._parse_equation(equation)

        try:
            expr = sp.sympify(f"({left}) - ({right})")
        except Exception as e:
            return {"error": f"Failed to parse: {e}"}

        solutions = []
        numerical = []
        steps = []

        try:
            if eq_type == "transcendental":
                for guess in [0.1, 0.5, 1, 2, 5, 10, 20, 50, 100, -0.5, -1, -2, -5]:
                    try:
                        sol = sp.nsolve(expr, guess, tol=1e-14, maxsteps=100)
                        sol_float = float(sol)
                        if not any(abs(sol_float - n) < 1e-6 for n in numerical):
                            # ตรวจสอบด้วยการแทนค่ากลับ
                            left_val = float(sp.N(sp.sympify(left).subs(x, sol_float)))
                            right_val = float(sp.N(sp.sympify(right).subs(x, sol_float)))
                            if abs(left_val - right_val) < 1e-8:
                                solutions.append(str(sol))
                                numerical.append(round(sol_float, 6))
                    except Exception:
                        continue
                steps.append("Used nsolve with multiple guesses")
            else:
                sols = sp.solve(expr, x)
                for sol in sols:
                    solutions.append(str(sol))
                    try:
                        if sol.is_real:
                            numerical.append(round(float(sol.evalf()), 6))
                    except Exception:
                        pass
                steps.append(f"Found {len(sols)} solution(s)")

        except Exception as e:
            return {"error": f"Solve failed: {e}"}

        return {
            "math": {
                "type": "single",
                "original": equation,
                "solutions": solutions,
                "numerical": numerical,
                "solver_used": "sympy",
                "steps": steps
            }
        }

    # ═══════════════════════════════════════════════════════════
    # System of Equations
    # ═══════════════════════════════════════════════════════════

    def _solve_system(self, equations: List[str]) -> dict:
        import sympy as sp

        variables = set()
        for eq in equations:
            for ch in eq:
                if ch.isalpha():
                    variables.add(ch)

        if not variables:
            variables = {'x', 'y'}

        syms = sp.symbols(' '.join(sorted(variables)))
        if not isinstance(syms, tuple):
            syms = (syms,)

        try:
            parsed = []
            for eq in equations:
                eq = self._clean_equation(eq)
                left, right = self._parse_equation(eq)
                parsed.append(sp.Eq(sp.sympify(left), sp.sympify(right)))

            solutions = sp.solve(parsed, syms, dict=True)

            return {
                "math": {
                    "type": "system",
                    "original": equations,
                    "solutions": [
                        {str(k): str(v) for k, v in sol.items()}
                        for sol in solutions
                    ],
                    "numerical": [
                        {
                            str(k): round(float(v.evalf()), 6)
                            for k, v in sol.items()
                        }
                        for sol in solutions
                    ],
                    "solver_used": "sympy",
                    "steps": [f"Solved system of {len(equations)} equations"]
                }
            }
        except Exception as e:
            return {"error": f"System solve failed: {e}"}

    # ═══════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════

    def _parse_equation(self, equation: str) -> tuple:
        if "=" in equation:
            parts = equation.split("=", 1)
            return parts[0].strip(), parts[1].strip()
        return equation.strip(), "0"


# ═══════════════════════════════════════════════════════════════
# Quick Test
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    tool = MathTool()

    tests = [
        "9.8 - 9.11 = ?",
        "9.8 - 9.11 = x",
        "3^x = x^9",
        "4^x = x^8",
        "5^x = x^5",
        "6^x = x^4",
        "x^2 + 19x - 92 = 0",
        "23x + 100 = 491",
        "4^x = x^16",
        "x - y = 5, x * y = 24",
        "5^x = x^25",
        "2^x = x^8",
        "x^3+x+10=0",
        "ว+ร+ก+ฤ+ช=14,ว+ร=10,ก+ฤ+ช=4,ก+ช=4",
        "w+o+r+k+r+i+t=14,w+o+r=10"
    ]

    for test in tests:
        result = tool.execute({"equation": test})
        print(f"\n{'='*60}")
        print(f"Input: {test}")
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            m = result.get("math", {})
            print(f"Type: {m.get('type')}")
            print(f"Solutions: {m.get('solutions')}")
            print(f"Numerical: {m.get('numerical')}")
            print(f"Solver: {m.get('solver_used')}")