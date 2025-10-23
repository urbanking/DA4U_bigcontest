# 새로운 Gemini 프롬프트 생성 함수

def generate_marketing_prompt(result):
    """간결하고 명확한 마케팅 보고서 생성 프롬프트"""
    
    persona_analysis = result.get("persona_analysis", {})
    risk_analysis = result.get("risk_analysis", {})
    strategies = result.get("marketing_strategies", [])
    
    store_code = result.get("store_code", "매장")
    persona_type = persona_analysis.get("persona_type", "")
    components = persona_analysis.get("components", {})
    detected_risks = risk_analysis.get("detected_risks", [])
    key_channels = persona_analysis.get("key_channels", [])
    
    # 위험 요소
    risk_details = "\n".join([
        f"- **{r.get('name', '')}** (우선순위: {r.get('priority', '')}): {r.get('description', '')}"
        for r in detected_risks
    ]) if detected_risks else "- 특별한 위험 요소 없음"
    
    # 추천 채널
    key_channels_text = "\n".join([f"- {ch}" for ch in key_channels]) if key_channels else "- 채널 정보 없음"
    
    # 전략 요약 (채널 확장)
    strategy_details = []
    for i, s in enumerate(strategies[:6]):
        channel_info = s.get('channel', '')
        
        # 채널 확장
        expanded = []
        if '디지털' in channel_info or '온라인' in channel_info:
            expanded.extend(['인스타그램', '네이버플레이스', '카카오맵'])
        if '배달' in channel_info:
            expanded.extend(['배달의민족', '쿠팡이츠'])
        if '오프라인' in channel_info or '매장' in channel_info:
            expanded.extend(['매장 POP', '전단지'])
        if 'SNS' in channel_info:
            expanded.extend(['인스타그램', '틱톡'])
        
        if not expanded:
            expanded = [channel_info]
        
        channel_str = ", ".join(set(expanded))
        
        strategy_details.append(
            f"**전략 {i+1}: {s.get('name', '')}**\n" +
            f"- 설명: {s.get('description', '')[:150]}\n" +
            f"- 채널: {channel_str}\n" +
            f"- 기간: {s.get('implementation_time', '')} / 예산: {s.get('budget_estimate', '')}"
        )
    
    strategy_summary = "\n\n".join(strategy_details)
    
    prompt = f"""
당신은 소상공인 마케팅 컨설턴트입니다. 아래 데이터를 바탕으로 실행 가능한 마케팅 보고서를 작성하세요.

## 📊 분석 데이터

**매장 정보**
- 매장: {store_code}
- 업종: {components.get('industry', '')} / 상권: {components.get('commercial_zone', '')}
- 페르소나: {persona_type}
- 주요 고객: {components.get('customer_demographics', {}).get('gender', '')} {components.get('customer_demographics', {}).get('age', '')} ({components.get('customer_type', '')})
- 배달 비중: {components.get('delivery_ratio', '')}

**위험 분석 (위험도: {risk_analysis.get('overall_risk_level', '')})**
{risk_details}

**추천 채널**
{key_channels_text}

**전략 요약**
{strategy_summary}

---

## 📝 작성 양식

아래 형식을 **정확히** 따라 작성하세요:

# 📊 마케팅 전략 종합 분석

## 📋 종합 결론

{store_code} 매장의 현황과 전략 방향성을 2-3문단으로 자연스럽게 서술하세요.
- 매장 위치, 상권 특성, 핵심 고객층
- 강점과 위험 요소
- 전반적인 마케팅 방향

## 📢 홍보 아이디어

위 전략을 바탕으로 **6가지 구체적인** 홍보 아이디어를 작성하세요.

**1. [아이디어 제목]**
- 내용: [2-3문장의 구체적 실행 방안]
- 채널: [인스타그램, 네이버플레이스 등 구체적 이름]
- 효과: [예상 효과]

(2~6번도 동일 형식)

## 🎯 타겟 전략

### 주 타겟
- 배경 연령: {components.get('customer_demographics', {}).get('age', '')}
- 주요 고객: {components.get('customer_demographics', {}).get('gender', '')} {components.get('customer_demographics', {}).get('age', '')}
- 고객유형: {components.get('customer_type', '')}
- 배달 비중: {components.get('delivery_ratio', '')}

### ⚠️ 위험 수준: {risk_analysis.get('overall_risk_level', '')}

**감지된 위험 요소:**
{risk_details}

## 📱 추천 마케팅 전략

우선순위별로 **4가지 전략**을 작성하세요.

### 전략 1: [전략명]

**📋 설명:** [3-4문장]

**⚡ 주요 전술:**
  • [전술 1]
  • [전술 2]

**🎯 예상 효과:** [효과]
**⏱️ 구현 기간:** [기간]
**💰 예산:** [예산]
**⭐ 우선순위:** 1

(전략 2-4도 동일)

## 📊 핵심 인사이트

3가지 핵심 포인트:

1. **[제목]**: [2-3문장]
2. **[제목]**: [2-3문장]
3. **[제목]**: [2-3문장]

## 🎯 다음 단계 제안

4가지 구체적 제안:

1. **[제목]**: [실행 방안 2-3문장]
2. **[제목]**: [실행 방안 2-3문장]
3. **[제목]**: [실행 방안 2-3문장]
4. **[제목]**: [실행 방안 2-3문장]

---

⚠️ **중요**
1. "다양한 채널" 금지 → **인스타그램, 네이버플레이스, 카카오맵, 배달의민족** 등 구체적 이름 사용
2. 위 데이터를 반드시 활용
3. 전문적이면서 이해하기 쉽게
4. 이모지 적절히 활용
5. 모든 제안은 즉시 실행 가능해야 함
"""
    
    return prompt
