from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import base64
from werkzeug.utils import secure_filename
import openai
from io import BytesIO
from PIL import Image
import requests
import re
import math

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = os.environ.get('SECRET_KEY', 'mater2-secret-key-2024')

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI API 키 설정 (환경 변수에서 가져오기)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encode_image(image_path):
    """이미지를 base64로 인코딩"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_mime_type(image_path):
    """이미지 파일의 MIME 타입 반환"""
    ext = image_path.lower().split('.')[-1]
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')

def extract_text_from_image(image_path):
    """이미지에서 텍스트 추출 (OCR 시도)"""
    try:
        # pytesseract가 설치되어 있으면 사용
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='kor+eng')
            return text.strip()
        except ImportError:
            # pytesseract가 없으면 이미지 정보만 반환
            return "이미지에서 텍스트를 자동으로 인식할 수 없습니다. 문제를 직접 입력해주세요."
    except Exception as e:
        return f"텍스트 추출 중 오류: {str(e)}"

def solve_linear_equation(equation_str):
    """일차방정식 풀이 (예: 2x + 5 = 13)"""
    try:
        original_eq = equation_str.strip()
        # x를 포함한 방정식 패턴 찾기
        eq_clean = equation_str.replace(' ', '').replace('×', '*').replace('÷', '/')
        
        # 등호 기준으로 분리
        if '=' not in eq_clean:
            return None
        
        left, right = eq_clean.split('=', 1)
        left_orig = left
        right_orig = right
        
        # x 항 찾기
        x_pattern = r'([+-]?\d*\.?\d*)x'
        x_matches = list(re.finditer(x_pattern, left))
        
        if not x_matches:
            return None
        
        # x의 계수 계산
        x_coeff = 0
        for match in x_matches:
            coeff_str = match.group(1)
            if coeff_str == '' or coeff_str == '+':
                x_coeff += 1
            elif coeff_str == '-':
                x_coeff -= 1
            else:
                x_coeff += float(coeff_str)
        
        # 상수항 계산
        left_const_str = left
        for match in reversed(x_matches):  # 역순으로 제거해야 인덱스 문제 없음
            left_const_str = left_const_str[:match.start()] + '0' + left_const_str[match.end():]
        
        # 상수항 값 계산
        try:
            # 연산자와 숫자만 남기기
            left_const_clean = re.sub(r'[^0-9+\-*/().]', '', left_const_str)
            if left_const_clean:
                left_const_val = eval(left_const_clean) if left_const_clean else 0
            else:
                left_const_val = 0
        except:
            left_const_val = 0
        
        try:
            right_val = float(right) if re.match(r'^-?\d+\.?\d*$', right) else eval(right)
        except:
            right_val = 0
        
        # ax + b = c -> x = (c - b) / a
        if abs(x_coeff) < 0.0001:
            return None
        
        answer = (right_val - left_const_val) / x_coeff
        
        # 풀이 과정 생성 (수식 중심)
        steps = []
        
        # 원래 방정식 표시
        original_left = left_orig.replace('*', '×').replace('/', '÷')
        original_right = right_orig.replace('*', '×').replace('/', '÷')
        
        # 1단계: 주어진 방정식
        steps.append(f"{original_left} = {original_right}")
        
        # 2단계: 상수항 이항 (수식으로 표현)
        const_result = right_val - left_const_val
        if abs(left_const_val) > 0.0001:
            if left_const_val > 0:
                # 양수 상수항 이항
                left_after = original_left.replace(f"+ {left_const_val}", "").replace(f"+{left_const_val}", "").replace(f"{left_const_val}", "")
                if left_after.startswith('+'):
                    left_after = left_after[1:].strip()
                steps.append(f"{left_after} = {original_right} - {left_const_val}")
            else:
                # 음수 상수항 이항
                left_after = original_left.replace(f"- {abs(left_const_val)}", "").replace(f"-{abs(left_const_val)}", "")
                steps.append(f"{left_after} = {original_right} - ({left_const_val})")
        
        # 3단계: 계산 (수식으로 표현)
        if x_coeff == 1:
            steps.append(f"x = {const_result}")
        elif x_coeff == -1:
            steps.append(f"-x = {const_result}")
            steps.append(f"x = -({const_result})")
            steps.append(f"x = {-const_result}")
            answer = -const_result
        else:
            # x 계수가 1이 아닌 경우
            if abs(const_result) < 0.0001:
                steps.append(f"{x_coeff}x = 0")
                steps.append(f"x = 0")
            else:
                steps.append(f"{x_coeff}x = {const_result}")
                if x_coeff != 1:
                    steps.append(f"x = {const_result} ÷ {x_coeff}")
                    if const_result % x_coeff == 0:
                        steps.append(f"x = {int(const_result // x_coeff)}")
                    else:
                        steps.append(f"x = {answer}")
                else:
                    steps.append(f"x = {answer}")
        
        return {
            'answer': answer,
            'steps': steps,
            'type': 'linear_equation',
            'original': original_eq
        }
    except Exception as e:
        return None

def solve_arithmetic(expression_str):
    """산술 연산 풀이 (예: 15 × 8 + 24 ÷ 3)"""
    try:
        original_expr = expression_str.strip()
        # 연산 기호 변환
        expr = expression_str.replace('×', '*').replace('÷', '/').replace(' ', '')
        
        # 안전한 계산 (간단한 수식만)
        if not re.match(r'^[0-9+\-*/().\s]+$', expr):
            return None
        
        # 단계별 계산 과정 생성 (수식 중심)
        steps = []
        current_expr = original_expr
        expr_work = expr
        
        # 곱셈/나눗셈 먼저
        mult_div_pattern = r'(\d+(?:\.\d+)?)\s*([*/])\s*(\d+(?:\.\d+)?)'
        step_num = 1
        while re.search(mult_div_pattern, expr_work):
            match = re.search(mult_div_pattern, expr_work)
            a, op, b = match.groups()
            a, b = float(a), float(b)
            if op == '*':
                temp_result = a * b
                result_str = str(int(temp_result) if temp_result.is_integer() else temp_result)
                # 원래 표현식에서 해당 부분 찾아서 교체
                if '×' in current_expr:
                    pattern = f"{int(a) if a.is_integer() else a} × {int(b) if b.is_integer() else b}"
                else:
                    pattern = f"{int(a) if a.is_integer() else a}*{int(b) if b.is_integer() else b}"
                steps.append(f"【{step_num}단계】 {current_expr}")
                current_expr = current_expr.replace(pattern, result_str, 1)
                steps.append(f"    = {current_expr}  (∵ {int(a) if a.is_integer() else a} × {int(b) if b.is_integer() else b} = {result_str})")
                expr_work = expr_work.replace(match.group(), result_str, 1)
                step_num += 1
            else:
                temp_result = a / b
                result_str = str(int(temp_result) if temp_result.is_integer() else temp_result)
                if '÷' in current_expr:
                    pattern = f"{int(a) if a.is_integer() else a} ÷ {int(b) if b.is_integer() else b}"
                else:
                    pattern = f"{int(a) if a.is_integer() else a}/{int(b) if b.is_integer() else b}"
                steps.append(f"【{step_num}단계】 {current_expr}")
                current_expr = current_expr.replace(pattern, result_str, 1)
                steps.append(f"    = {current_expr}  (∵ {int(a) if a.is_integer() else a} ÷ {int(b) if b.is_integer() else b} = {result_str})")
                expr_work = expr_work.replace(match.group(), result_str, 1)
                step_num += 1
        
        # 덧셈/뺄셈
        add_sub_pattern = r'(\d+(?:\.\d+)?)\s*([+-])\s*(\d+(?:\.\d+)?)'
        while re.search(add_sub_pattern, expr_work):
            match = re.search(add_sub_pattern, expr_work)
            a, op, b = match.groups()
            a, b = float(a), float(b)
            if op == '+':
                temp_result = a + b
                result_str = str(int(temp_result) if temp_result.is_integer() else temp_result)
                pattern = f"{int(a) if a.is_integer() else a} + {int(b) if b.is_integer() else b}"
                steps.append(f"【{step_num}단계】 {current_expr}")
                current_expr = current_expr.replace(pattern, result_str, 1)
                steps.append(f"    = {current_expr}  (∵ {int(a) if a.is_integer() else a} + {int(b) if b.is_integer() else b} = {result_str})")
                expr_work = expr_work.replace(match.group(), result_str, 1)
                step_num += 1
            else:
                temp_result = a - b
                result_str = str(int(temp_result) if temp_result.is_integer() else temp_result)
                pattern = f"{int(a) if a.is_integer() else a} - {int(b) if b.is_integer() else b}"
                steps.append(f"【{step_num}단계】 {current_expr}")
                current_expr = current_expr.replace(pattern, result_str, 1)
                steps.append(f"    = {current_expr}  (∵ {int(a) if a.is_integer() else a} - {int(b) if b.is_integer() else b} = {result_str})")
                expr_work = expr_work.replace(match.group(), result_str, 1)
                step_num += 1
        
        result = eval(expr_work)
        
        return {
            'answer': int(result) if isinstance(result, float) and result.is_integer() else result,
            'steps': steps,
            'type': 'arithmetic',
            'original': original_expr
        }
    except Exception as e:
        return None

def solve_math_problem_local(problem_text):
    """로컬에서 수학 문제 풀이 시도 (실제 계산)"""
    if not problem_text or len(problem_text.strip()) < 3:
        problem_text = "문제를 입력해주세요"
    
    problem_clean = problem_text.strip()
    
    # 방정식 풀이 시도
    equation_result = solve_linear_equation(problem_clean)
    if equation_result:
        answer = equation_result['answer']
        steps = equation_result['steps']
        original = equation_result.get('original', problem_clean)
        
        solution1 = f"""풀이 방법 1 (일차방정식 풀이):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【문제】 {original}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for i, step in enumerate(steps, 1):
            solution1 += f"【{i}단계】 {step}\n\n"
        
        solution1 += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 최종 답: x = {answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        # answer를 명확히 반환
        final_answer = answer

        solution2 = f"""풀이 방법 2 (검증 방법):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【문제】 {original}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1단계】 답을 원래 식에 대입하여 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
x = {answer}를 원래 방정식에 대입합니다.

"""
        
        # 원래 방정식에서 x에 답 대입
        if '=' in original:
            left, right = original.split('=', 1)
            left_clean = left.strip()
            right_clean = right.strip()
            left_sub = left_clean.replace('x', f'({answer})').replace('×', '*').replace('÷', '/')
            right_clean_eval = right_clean.replace('×', '*').replace('÷', '/')
            try:
                left_val = eval(left_sub)
                right_val = eval(right_clean_eval)
                solution2 += f"【대입】 {left_clean.replace('x', f'({answer})')} = {right_clean}\n\n"
                solution2 += f"【계산】 좌변 = {left_val}\n"
                solution2 += f"        우변 = {right_val}\n\n"
                if abs(left_val - right_val) < 0.0001:
                    solution2 += f"✅ {left_val} = {right_val} 이므로 답이 맞습니다!\n\n"
                else:
                    solution2 += f"⚠️ {left_val} ≠ {right_val} 다시 확인해주세요.\n\n"
            except Exception as e:
                solution2 += f"검증 계산 중 오류가 발생했습니다.\n\n"
        
        solution2 += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 최종 답: x = {answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        concept = f"""📚 개념 설명:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【일차방정식의 풀이 원리】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

일차방정식 ax + b = c 형태의 방정식을 풀 때:

1. 등식의 성질 이용
   • 양변에 같은 수를 더하거나 빼도 등식은 성립합니다.
   • 양변에 0이 아닌 같은 수를 곱하거나 나눠도 등식은 성립합니다.

2. 이항
   • 한 변의 항을 부호를 바꿔서 다른 변으로 옮기는 것을 이항이라고 합니다.
   • 예: 2x + 5 = 13 → 2x = 13 - 5

3. 계수로 나누기
   • x의 계수로 양변을 나누어 x의 값을 구합니다.
   • 예: 2x = 8 → x = 8 ÷ 2 = 4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 학습 팁: 방정식을 풀 때는 항상 답을 원래 식에 
   대입하여 검증하는 습관을 기르세요."""

        similar_problem = f"""🔢 유사한 문제:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

다음은 이 문제와 유사한 일차방정식 문제들입니다:

1. 3x + 7 = 22
   → x = ?

2. 5x - 4 = 11
   → x = ?

3. 2x + 3 = 4x - 1
   → x = ?

4. x/2 + 5 = 9
   → x = ?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 연습 팁: 위 문제들을 직접 풀어보면서 
   일차방정식 풀이를 익혀보세요."""

        return {
            'solution1': solution1,
            'solution2': solution2,
            'concept': concept,
            'similar_problem': similar_problem,
            'success': True,
            'answer': float(final_answer) if isinstance(final_answer, (int, float)) else final_answer
        }
    
    # 산술 연산 풀이 시도
    arithmetic_result = solve_arithmetic(problem_clean)
    if arithmetic_result:
        answer = arithmetic_result['answer']
        steps = arithmetic_result['steps']
        original = arithmetic_result.get('original', problem_clean)
        
        solution1 = f"""풀이 방법 1 (연산 순서에 따른 풀이):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【문제】 {original}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

연산 순서: 곱셈/나눗셈 → 덧셈/뺄셈

"""
        for step in steps:
            solution1 += f"{step}\n\n"
        
        solution1 += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 최종 답: {answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        solution2 = f"""풀이 방법 2 (괄호를 이용한 풀이):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【문제】 {problem_clean}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1단계】 연산 순서를 명확히 하기 위해 괄호 사용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
곱셈과 나눗셈을 먼저 계산하기 위해 괄호로 묶어 생각합니다.

"""
        
        # 곱셈/나눗셈 부분 강조
        expr = problem_clean.replace('×', '*').replace('÷', '/')
        solution2 += f"원래 식: {problem_clean}\n\n"
        solution2 += "곱셈/나눗셈을 먼저 계산:\n"
        
        for step in steps[1:-1]:  # 첫 번째와 마지막 제외
            solution2 += f"  {step}\n"
        
        solution2 += f"\n【2단계】 최종 계산\n"
        solution2 += f"  {steps[-1]}\n\n"
        solution2 += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 최종 답: {answer}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        concept = f"""📚 개념 설명:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【연산 순서 (연산 우선순위)】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

수학에서 연산을 수행할 때는 다음 순서를 따릅니다:

1. 괄호 ( )
   • 괄호 안의 계산을 가장 먼저 합니다.

2. 곱셈(×)과 나눗셈(÷)
   • 곱셈과 나눗셈은 덧셈과 뺄셈보다 먼저 계산합니다.
   • 곱셈과 나눗셈이 함께 있으면 왼쪽부터 순서대로 계산합니다.

3. 덧셈(+)과 뺄셈(-)
   • 곱셈과 나눗셈을 모두 계산한 후 덧셈과 뺄셈을 계산합니다.
   • 덧셈과 뺄셈이 함께 있으면 왼쪽부터 순서대로 계산합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 기억하기: "곱셈/나눗셈 먼저, 덧셈/뺄셈 나중에" """

        similar_problem = f"""🔢 유사한 문제:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

다음은 연산 순서를 연습할 수 있는 문제들입니다:

1. 12 + 4 × 3 = ?
2. 20 - 8 ÷ 2 = ?
3. 6 × 3 + 10 ÷ 2 = ?
4. 15 + 3 × 4 - 7 = ?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 연습 팁: 각 문제를 단계별로 풀어보면서 
   연산 순서를 익혀보세요."""

        return {
            'solution1': solution1,
            'solution2': solution2,
            'concept': concept,
            'similar_problem': similar_problem,
            'success': True,
            'answer': float(answer) if isinstance(answer, (int, float)) else answer
        }
    
    # 패턴을 찾지 못한 경우 일반 가이드 제공
    solution1 = f"""풀이 방법 1 (일반적인 방법):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【문제】 {problem_clean}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1단계】 문제 이해 및 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 주어진 문제를 천천히 읽고 이해합니다.
• 문제에서 요구하는 답이 무엇인지 파악합니다.
• 문제에 주어진 모든 정보를 확인합니다.

【2단계】 주어진 조건 정리
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 문제에 나온 숫자, 변수, 수식을 정리합니다.
• 필요한 공식이나 개념을 떠올립니다.
• 문제의 핵심을 파악합니다.

【3단계】 풀이 전략 수립
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 어떤 방법으로 문제를 풀지 결정합니다.
• 단계별 풀이 계획을 세웁니다.
• 계산 순서를 정합니다.

【4단계】 단계별 계산 수행
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 계획에 따라 차근차근 계산합니다.
• 각 단계의 중간 결과를 확인합니다.
• 실수를 하지 않도록 주의합니다.

【5단계】 답 검증 및 확인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 계산 결과가 논리적으로 맞는지 확인합니다.
• 문제의 조건을 모두 만족하는지 검토합니다.
• 최종 답을 명확히 제시합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 팁: 문제를 더 명확하게 입력해주시면 
   (예: "2x + 5 = 13" 또는 "15 × 8 + 24 ÷ 3")
   단계별 수식과 함께 정확한 답을 제공할 수 있습니다."""

    solution2 = f"""풀이 방법 2 (대안적인 접근):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【문제】 {problem_clean}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1단계】 다른 관점에서 문제 바라보기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 문제를 처음 보는 시각과 다르게 접근합니다.
• 대안적인 풀이 방법을 생각해봅니다.
• 더 간단하거나 효율적인 방법이 있는지 고민합니다.

【2단계】 문제 시각화 및 도식화
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 문제를 그림, 표, 그래프 등으로 표현합니다.
• 시각적으로 문제를 이해합니다.
• 관계를 명확히 파악합니다.

【3단계】 대안적 풀이 방법 적용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 선택한 대안 방법으로 단계별 풀이합니다.
• 각 단계를 상세히 설명합니다.
• 왜 이 방법을 선택했는지 설명합니다.

【4단계】 결과 비교 및 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 풀이 결과를 다른 방법과 비교합니다.
• 두 방법의 결과가 일치하는지 확인합니다.
• 더 나은 방법이 무엇인지 평가합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 팁: 문제를 더 명확하게 입력해주시면 
   (예: "2x + 5 = 13" 또는 "15 × 8 + 24 ÷ 3")
   단계별 수식과 함께 정확한 답을 제공할 수 있습니다."""
    solution1 = """풀이 방법 1 (일반적인 방법):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1단계】 문제 이해 및 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 주어진 문제를 천천히 읽고 이해합니다.
• 문제에서 요구하는 답이 무엇인지 파악합니다.
• 문제에 주어진 모든 정보를 확인합니다.

【2단계】 주어진 조건 정리
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 문제에 나온 숫자, 변수, 수식을 정리합니다.
• 필요한 공식이나 개념을 떠올립니다.
• 문제의 핵심을 파악합니다.

【3단계】 풀이 전략 수립
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 어떤 방법으로 문제를 풀지 결정합니다.
• 단계별 풀이 계획을 세웁니다.
• 계산 순서를 정합니다.

【4단계】 단계별 계산 수행
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 계획에 따라 차근차근 계산합니다.
• 각 단계의 중간 결과를 확인합니다.
• 실수를 하지 않도록 주의합니다.

【5단계】 답 검증 및 확인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 계산 결과가 논리적으로 맞는지 확인합니다.
• 문제의 조건을 모두 만족하는지 검토합니다.
• 최종 답을 명확히 제시합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 팁: 문제를 풀 때는 각 단계를 명확히 구분하여 
   풀이하는 것이 중요합니다. 실수를 줄이고 
   풀이 과정을 다시 확인할 수 있습니다."""

    solution2 = """풀이 방법 2 (대안적인 접근):

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【1단계】 다른 관점에서 문제 바라보기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 문제를 처음 보는 시각과 다르게 접근합니다.
• 대안적인 풀이 방법을 생각해봅니다.
• 더 간단하거나 효율적인 방법이 있는지 고민합니다.

【2단계】 문제 시각화 및 도식화
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 문제를 그림, 표, 그래프 등으로 표현합니다.
• 시각적으로 문제를 이해합니다.
• 관계를 명확히 파악합니다.

【3단계】 대안적 풀이 방법 적용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 선택한 대안 방법으로 단계별 풀이합니다.
• 각 단계를 상세히 설명합니다.
• 왜 이 방법을 선택했는지 설명합니다.

【4단계】 결과 비교 및 검증
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 풀이 결과를 다른 방법과 비교합니다.
• 두 방법의 결과가 일치하는지 확인합니다.
• 더 나은 방법이 무엇인지 평가합니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 팁: 한 문제를 여러 방법으로 풀어보면 
   수학적 사고력이 향상됩니다. 다양한 접근 
   방법을 익혀두면 유사한 문제를 더 쉽게 
   풀 수 있습니다."""

    concept = """📚 개념 설명:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

이 수학 문제를 풀기 위해 필요한 주요 개념들:

【1】 기본 연산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 덧셈(+), 뺄셈(-), 곱셈(×), 나눗셈(÷)
• 연산 순서: 괄호 → 곱셈/나눗셈 → 덧셈/뺄셈
• 음수와 양수의 계산 규칙

【2】 방정식과 부등식
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 미지수(x, y 등)를 포함한 식
• 등식의 성질: 양변에 같은 수를 더하거나 빼도 등식 성립
• 일차방정식, 이차방정식의 풀이 방법

【3】 함수와 그래프
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 함수의 개념: 입력값에 대한 출력값의 관계
• 일차함수, 이차함수, 지수함수 등
• 그래프를 통한 함수의 이해

【4】 기하학
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 도형의 성질과 공식
• 넓이, 둘레, 부피 계산
• 삼각형, 사각형, 원 등의 특성

【5】 통계와 확률
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 평균, 중앙값, 최빈값
• 확률의 기본 개념
• 데이터 분석 방법

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 학습 팁: 각 개념을 이해한 후, 다양한 문제에 
   적용해보면서 실력을 키워나가세요."""

    similar_problem = """🔢 유사한 문제 예시:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

다양한 유형의 수학 문제 예시:

【기본 연산 문제】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "15 × 8 + 24 ÷ 3 = ?"
• "100 - 25 × 2 + 50 = ?"

【방정식 문제】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "2x + 5 = 13일 때, x의 값은?"
• "3x - 7 = 2x + 3일 때, x의 값은?"

【기하 문제】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "한 변의 길이가 5cm인 정사각형의 넓이는?"
• "반지름이 3cm인 원의 넓이는?"

【함수 문제】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• "f(x) = x² + 3x - 4일 때, f(2)의 값은?"
• "g(x) = 2x + 1일 때, g(5)의 값은?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 연습 팁: 유사한 문제를 반복해서 풀어보면 
   문제 해결 능력이 향상됩니다."""

    return {
        'solution1': solution1,
        'solution2': solution2,
        'concept': concept,
        'similar_problem': similar_problem,
        'success': True,
        'demo': True
    }

def solve_math_problem_with_ai(image_path, problem_text=None):
    """AI를 사용하여 수학 문제 풀이 (2가지 방법)"""
    try:
        # 이미지를 base64로 인코딩
        base64_image = encode_image(image_path)
        mime_type = get_image_mime_type(image_path)
        
        # OpenAI Vision API를 사용하여 문제 인식 및 풀이
        if OPENAI_API_KEY:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # 첫 번째 풀이 방법
            response1 = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """이 이미지의 수학 문제를 분석하고 풀이해주세요. 
                                반드시 다음 형식으로 답변해주세요:
                                1. 문제를 정확히 파악하고
                                2. 각 단계별로 구체적인 수식과 계산 과정을 보여주고
                                3. 중간 계산 결과를 명시하고
                                4. 최종 답을 명확히 제시해주세요.
                                
                                풀이 방법 1: 일반적인 방법으로 단계별 수식과 함께 풀어주세요.
                                예시 형식:
                                【1단계】 문제: 2x + 5 = 13
                                【2단계】 이항: 2x = 13 - 5
                                【3단계】 계산: 2x = 8
                                【4단계】 나누기: x = 8 ÷ 2
                                【5단계】 정답: x = 4"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500
            )
            
            # 두 번째 풀이 방법
            response2 = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """이 이미지의 수학 문제를 분석하고 풀이해주세요. 
                                반드시 다음 형식으로 답변해주세요:
                                1. 문제를 다른 관점에서 접근하고
                                2. 각 단계별로 구체적인 수식과 계산 과정을 보여주고
                                3. 중간 계산 결과를 명시하고
                                4. 최종 답을 명확히 제시해주세요.
                                
                                풀이 방법 2: 다른 접근 방법이나 대안적인 풀이법으로 단계별 수식과 함께 풀어주세요.
                                예시 형식:
                                【1단계】 문제: 2x + 5 = 13
                                【2단계】 다른 방법: 양변에서 5를 빼기
                                【3단계】 계산: 2x = 8
                                【4단계】 양변을 2로 나누기: x = 4
                                【5단계】 정답: x = 4"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500
            )
            
            # 개념 설명
            concept_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """이 수학 문제에서 사용된 주요 개념과 원리를 자세히 설명해주세요.
                                학생이 이해하기 쉽게 설명해주세요."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            # 유사 문제 생성
            similar_problem_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """이 수학 문제와 비슷한 난이도의 유사한 문제를 하나 만들어주세요.
                                문제만 제시해주세요."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return {
                'solution1': response1.choices[0].message.content,
                'solution2': response2.choices[0].message.content,
                'concept': concept_response.choices[0].message.content,
                'similar_problem': similar_problem_response.choices[0].message.content,
                'success': True
            }
        else:
            # API 키가 없을 경우 로컬 풀이 시도
            if problem_text:
                return solve_math_problem_local(problem_text)
            else:
                # 이미지에서 텍스트 추출 시도
                extracted_text = extract_text_from_image(image_path)
                # 추출된 텍스트가 의미있는지 확인
                if extracted_text and len(extracted_text) > 5 and "이미지에서 텍스트를" not in extracted_text:
                    return solve_math_problem_local(extracted_text)
                else:
                    return solve_math_problem_local("문제를 직접 입력해주세요")
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('mater2_index.html')

@app.route('/api/solve', methods=['POST'])
def solve_problem():
    """수학 문제 풀이 API"""
    try:
        problem_text = request.form.get('problem_text', '').strip()
        
        # 텍스트가 있으면 먼저 로컬 풀이 시도 (빠른 응답)
        if problem_text:
            result = solve_math_problem_local(problem_text)
            if result and result.get('success') and result.get('answer') is not None:
                return jsonify(result)
        
        # 이미지 파일이 있는 경우
        if 'image' in request.files:
            file = request.files['image']
            
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # 텍스트가 없으면 이미지에서 텍스트 추출 시도
                if not problem_text:
                    extracted_text = extract_text_from_image(filepath)
                    if extracted_text and len(extracted_text) > 5 and "이미지에서 텍스트를" not in extracted_text:
                        problem_text = extracted_text
                
                # 텍스트가 있으면 로컬 풀이 먼저 시도
                if problem_text:
                    result = solve_math_problem_local(problem_text)
                    if result and result.get('success') and result.get('answer') is not None:
                        try:
                            os.remove(filepath)
                        except:
                            pass
                        return jsonify(result)
                
                # AI로 문제 풀이 (API 키가 있는 경우)
                result = solve_math_problem_with_ai(filepath, problem_text)
                
                # 임시 파일 삭제
                try:
                    os.remove(filepath)
                except:
                    pass
                
                return jsonify(result)
        
        # 텍스트만 있는 경우 (이미 처리됨)
        if problem_text:
            result = solve_math_problem_local(problem_text)
            return jsonify(result)
        
        return jsonify({'success': False, 'error': '이미지 파일 또는 문제 텍스트를 입력해주세요.'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
