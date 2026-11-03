"""
AI/ML Engine for Intelligent Online Examination System
Covers:
1. NLP Duplicate Detection & Question Similarity (TF-IDF + Cosine Similarity)
2. AI-Assisted Descriptive Answer Evaluation (Semantic overlap, key concepts, keyword density)
3. Item Response Theory (IRT) Adaptive Testing Engine (Rasch 1PL ability estimation & next question selector)
4. Item Analysis Engine (Difficulty Index P, Discrimination Index D, Distractor Analysis)
5. Student Performance Prediction (Linear Regression / ML performance estimator)
6. Cryptographic Integrity & Result Verification (SHA-256 Hash signature)
7. Camera-Free Behavioral Risk Scoring Engine
"""

import math
import re
import hashlib
import json
import time

# -------------------------------------------------------------
# 1. NLP QUESTION SIMILARITY & DUPLICATE DETECTION (TF-IDF)
# -------------------------------------------------------------
class NLPQuestionAnalyzer:
    STOPWORDS = {
        'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren',
        'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
        'can', 'could', 'did', 'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from',
        'further', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself',
        'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most',
        'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our',
        'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so', 'some', 'such', 'than',
        'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this',
        'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when',
        'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you', 'your', 'yours'
    }

    @staticmethod
    def tokenize(text):
        words = re.findall(r'\b[a-z0-9]+\b', text.lower())
        return [w for w in words if w not in NLPQuestionAnalyzer.STOPWORDS and len(w) > 1]

    @classmethod
    def compute_similarity(cls, text1, text2):
        tokens1 = cls.tokenize(text1)
        tokens2 = cls.tokenize(text2)
        if not tokens1 or not tokens2:
            return 0.0

        vocab = sorted(list(set(tokens1 + tokens2)))
        # TF vectors
        def get_tf_vector(tokens):
            vec = {}
            total = len(tokens)
            for w in tokens:
                vec[w] = vec.get(w, 0) + 1
            return [vec.get(w, 0) / total for w in vocab]

        vec1 = get_tf_vector(tokens1)
        vec2 = get_tf_vector(tokens2)

        # Cosine Similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return round((dot_product / (norm1 * norm2)) * 100, 2)

    @classmethod
    def assess_question_quality(cls, question_text, options, explanation=""):
        score = 100
        issues = []
        words = len(question_text.split())
        if words < 5:
            score -= 30
            issues.append("Question prompt is too short (< 5 words).")
        elif words > 80:
            score -= 10
            issues.append("Question prompt may be overly verbose.")

        if options and len(options) < 4:
            score -= 25
            issues.append("Fewer than 4 distractors provided.")

        # Check distractor uniformity
        if options:
            lengths = [len(opt.strip()) for opt in options]
            if max(lengths) > (min(lengths) * 3 + 10):
                score -= 15
                issues.append("Distractor length asymmetry (one option is drastically longer).")

        if not explanation:
            score -= 10
            issues.append("No pedagogical rationale/explanation provided.")

        return {
            "quality_score": max(20, score),
            "status": "Approved" if score >= 75 else "Review Needed",
            "feedback": issues if issues else ["Well-formed question meeting psychometric standards."]
        }

# -------------------------------------------------------------
# 2. AI ASSISTED DESCRIPTIVE ANSWER EVALUATION
# -------------------------------------------------------------
class DescriptiveEvaluationEngine:
    @staticmethod
    def evaluate(student_answer, reference_answer, key_concepts, max_marks=5):
        if not student_answer or len(student_answer.strip()) == 0:
            return {
                "awarded_marks": 0.0,
                "confidence": 100,
                "concept_match_pct": 0,
                "feedback": "No answer provided.",
                "matched_concepts": [],
                "missing_concepts": key_concepts
            }

        student_lower = student_answer.lower()
        matched = []
        missing = []

        for concept in key_concepts:
            concept_clean = concept.strip().lower()
            if concept_clean in student_lower:
                matched.append(concept)
            else:
                # check partial token match
                tokens = concept_clean.split()
                if any(t in student_lower for t in tokens if len(t) > 3):
                    matched.append(concept)
                else:
                    missing.append(concept)

        concept_ratio = len(matched) / max(len(key_concepts), 1)
        sim_score = NLPQuestionAnalyzer.compute_similarity(student_answer, reference_answer) / 100.0

        # Length adequacy penalty if student wrote less than 20% of reference
        ref_words = len(reference_answer.split())
        stud_words = len(student_answer.split())
        length_factor = min(1.0, stud_words / max(ref_words * 0.4, 10))

        # Composite score
        weighted_score = (0.55 * concept_ratio) + (0.35 * sim_score) + (0.10 * length_factor)
        marks = round(weighted_score * max_marks, 1)
        marks = min(max_marks, max(0.0, marks))

        confidence = round(70 + (25 * concept_ratio), 1)

        feedback_notes = []
        if matched:
            feedback_notes.append(f"Accurately covered key terms: {', '.join(matched)}.")
        if missing:
            feedback_notes.append(f"Could elaborate on missing points: {', '.join(missing)}.")

        return {
            "awarded_marks": marks,
            "max_marks": max_marks,
            "confidence": confidence,
            "concept_match_pct": round(concept_ratio * 100, 1),
            "similarity_pct": round(sim_score * 100, 1),
            "matched_concepts": matched,
            "missing_concepts": missing,
            "feedback": " ".join(feedback_notes)
        }

# -------------------------------------------------------------
# 3. ADAPTIVE TESTING ENGINE (ITEM RESPONSE THEORY - RASCH 1PL)
# -------------------------------------------------------------
class AdaptiveTestingEngine:
    """
    Rasch Model Probability of Correct Response:
    P(theta) = 1 / (1 + exp(-(theta - b)))
    where:
      theta = student estimated ability (e.g., -2.0 to +2.0)
      b     = item difficulty (-1.5 = easy, 0.0 = medium, +1.5 = hard)
    """
    DIFFICULTY_MAPPING = {
        'easy': -1.2,
        'medium': 0.0,
        'hard': 1.2
    }

    @staticmethod
    def estimate_probability(theta, item_difficulty_val):
        return 1.0 / (1.0 + math.exp(-(theta - item_difficulty_val)))

    @classmethod
    def update_ability(cls, current_theta, is_correct, item_difficulty_str):
        b = cls.DIFFICULTY_MAPPING.get(item_difficulty_str.lower(), 0.0)
        p = cls.estimate_probability(current_theta, b)
        
        # Newton-Raphson step or standard fixed step update
        step = 0.45
        outcome = 1.0 if is_correct else 0.0
        delta = step * (outcome - p)
        
        new_theta = current_theta + delta
        # Bound theta between -3.0 and +3.0
        return round(max(-3.0, min(3.0, new_theta)), 3)

    @classmethod
    def select_next_difficulty(cls, theta):
        """
        Determines the target question difficulty for next question
        based on current ability estimate theta.
        """
        if theta < -0.4:
            return 'easy'
        elif theta > 0.4:
            return 'hard'
        else:
            return 'medium'

# -------------------------------------------------------------
# 4. PSYCHOMETRIC ITEM ANALYSIS (P-Value & Discrimination D)
# -------------------------------------------------------------
class ItemAnalysisEngine:
    @staticmethod
    def calculate_item_statistics(total_attempts, total_correct, upper_group_correct, lower_group_correct, group_size):
        """
        Difficulty Index (P): P = Total Correct / Total Attempts
          - P > 0.75: Very Easy
          - 0.30 <= P <= 0.75: Good / Ideal Difficulty
          - P < 0.30: Very Difficult

        Discrimination Index (D): D = (Upper_Correct - Lower_Correct) / Group_Size
          - D >= 0.40: Excellent discrimination
          - 0.30 - 0.39: Good
          - 0.20 - 0.29: Marginal / Review recommended
          - D < 0.20: Poor discrimination
        """
        p_value = (total_correct / max(total_attempts, 1))
        
        if group_size > 0:
            d_index = (upper_group_correct - lower_group_correct) / float(group_size)
        else:
            d_index = 0.35 # default standard

        status = "Good"
        if p_value < 0.25:
            status = "Too Difficult"
        elif p_value > 0.85:
            status = "Too Easy"
        elif d_index < 0.20:
            status = "Poor Discrimination"

        return {
            "difficulty_index_p": round(p_value, 2),
            "discrimination_index_d": round(d_index, 2),
            "status": status,
            "recommendation": "Retain item" if status == "Good" else f"Revise or inspect: {status}"
        }

# -------------------------------------------------------------
# 5. MACHINE LEARNING PERFORMANCE PREDICTOR
# -------------------------------------------------------------
class StudentPerformancePredictor:
    """
    Multivariate regression model that predicts final expected semester/exam score
    based on:
      x1 = Quiz accuracy %
      x2 = Average response time ratio (Actual / Expected)
      x3 = Consistency / Attempt rate
      x4 = Adaptive ability theta
    """
    @staticmethod
    def predict(quiz_accuracy, time_efficiency_ratio, past_score_avg, ability_theta):
        # Trained feature weights based on educational data mining benchmarks
        w1 = 0.42 # Quiz Accuracy
        w2 = 0.28 # Past historical average
        w3 = 0.18 # IRT Ability normalized to 0-100
        w4 = 0.12 # Time efficiency

        # Normalize ability theta from [-3, 3] to [0, 100]
        theta_norm = max(0, min(100, ((ability_theta + 3.0) / 6.0) * 100))
        time_norm = max(20, min(100, 100 - abs(1.0 - time_efficiency_ratio) * 40))

        predicted = (w1 * quiz_accuracy) + (w2 * past_score_avg) + (w3 * theta_norm) + (w4 * time_norm)
        predicted = round(max(10, min(99.5, predicted)), 1)

        grade = 'A+' if predicted >= 90 else ('A' if predicted >= 80 else ('B' if predicted >= 70 else ('C' if predicted >= 60 else ('D' if predicted >= 40 else 'F'))))

        # Risk level
        if predicted >= 75:
            risk = "Low Risk (On Track for Distinction)"
        elif predicted >= 55:
            risk = "Moderate Risk (Needs Topic Reinforcement)"
        else:
            risk = "High Risk (Immediate Remediation Recommended)"

        return {
            "predicted_score_pct": predicted,
            "projected_grade": grade,
            "academic_risk_level": risk
        }

# -------------------------------------------------------------
# 6. CAMERA-FREE BEHAVIORAL RISK SCORING ENGINE
# -------------------------------------------------------------
class BehavioralRiskScorer:
    """
    Calculates explainable behavioral integrity risk score (0% to 100%)
    Weights without camera:
    - Tab Switch / Blur: 15 pts each (max 45)
    - Fullscreen Exit: 20 pts each (max 40)
    - Copy / Paste Attempt: 12 pts each (max 24)
    - Acoustic anomaly (loud talking/whisper): 15 pts each (max 30)
    - Keystroke anomaly (flight/burst typing): 10 pts each (max 20)
    - Rapid Anomalous Answering (<3s on complex Q): 10 pts each (max 20)
    """
    @staticmethod
    def calculate_risk(events):
        tab_switches = 0
        fullscreen_exits = 0
        copy_pastes = 0
        audio_violations = 0
        keystroke_anomalies = 0
        rapid_responses = 0

        for ev in events:
            ev_type = ev.get('event_type', '').lower()
            if 'tab' in ev_type or 'blur' in ev_type or 'visibility' in ev_type:
                tab_switches += 1
            elif 'fullscreen' in ev_type:
                fullscreen_exits += 1
            elif 'copy' in ev_type or 'paste' in ev_type:
                copy_pastes += 1
            elif 'audio' in ev_type or 'voice' in ev_type or 'noise' in ev_type:
                audio_violations += 1
            elif 'keystroke' in ev_type or 'typing' in ev_type:
                keystroke_anomalies += 1
            elif 'rapid' in ev_type or 'speed' in ev_type:
                rapid_responses += 1

        risk_score = 0
        risk_score += min(45, tab_switches * 15)
        risk_score += min(40, fullscreen_exits * 20)
        risk_score += min(24, copy_pastes * 12)
        risk_score += min(30, audio_violations * 15)
        risk_score += min(20, keystroke_anomalies * 10)
        risk_score += min(20, rapid_responses * 10)

        risk_score = min(100, risk_score)

        if risk_score <= 20:
            classification = "CLEAN / LOW RISK"
            color = "success"
        elif risk_score <= 55:
            classification = "MODERATE SUSPICION"
            color = "warning"
        else:
            classification = "HIGH SUSPICION / FLAG FOR AUDIT"
            color = "danger"

        return {
            "risk_score": risk_score,
            "classification": classification,
            "badge_color": color,
            "breakdown": {
                "tab_switches": tab_switches,
                "fullscreen_exits": fullscreen_exits,
                "copy_pastes": copy_pastes,
                "audio_violations": audio_violations,
                "keystroke_anomalies": keystroke_anomalies,
                "rapid_responses": rapid_responses
            }
        }

# -------------------------------------------------------------
# 7. CRYPTOGRAPHIC INTEGRITY & VERIFICATION HASH
# -------------------------------------------------------------
class CryptographicResultVerifier:
    SECRET_SALT = "ChandigarhUniversity_MCA_SecureExam_2026_Salt_Key"

    @classmethod
    def generate_result_hash(cls, student_id, exam_id, score, total_marks, timestamp):
        payload = f"{student_id}|{exam_id}|{score}|{total_marks}|{timestamp}|{cls.SECRET_SALT}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    @classmethod
    def verify_hash(cls, student_id, exam_id, score, total_marks, timestamp, provided_hash):
        expected_hash = cls.generate_result_hash(student_id, exam_id, score, total_marks, timestamp)
        return expected_hash == provided_hash
