import pandas as pd
import re

# 1. 데이터 로드 및 결제 카테고리 필터링
df = pd.read_csv('cs2_data_ko.csv')
payment_df = df[df['카테고리'] == '결제'].copy()

# 2. 중복 제거 (문의와 답변이 모두 동일한 경우)
payment_df = payment_df.drop_duplicates(subset=['문의 내용', '응답'])

# 3. 비속어 제거
profanities = ['씨발', '개새끼', '미친', '지랄', '병신', '존나', '썅']
pattern = '|'.join(profanities)
profanity_mask = payment_df['문의 내용'].str.contains(pattern, na=False) | payment_df['응답'].str.contains(pattern, na=False)
payment_df = payment_df[~profanity_mask]

# 4. 공백 및 줄바꿈 제거
payment_df['문의 내용'] = payment_df['문의 내용'].str.replace(r'\s+', ' ', regex=True).str.strip()
payment_df['응답'] = payment_df['응답'].str.replace(r'\s+', ' ', regex=True).str.strip()

# 5. Placeholder 매핑 (결제 및 연관 ERD 기준)
placeholder_mapping = {
    r'\{\{[Oo]rder [Nn]umber\}\}': '{order_id}',
    r'\{\{Client Name\}\}': '{name}',
    r'\{\{Client Full Name\}\}': '{name}',
    r'\{\{Client First Name\}\}': '{name}',
    r'\{\{Client Last Name\}\}': '{name}',
    r'\{\{Full Name\}\}': '{name}',
    r'\{\{Person Name\}\}': '{name}'
}

for pattern_str, repl in placeholder_mapping.items():
    payment_df['문의 내용'] = payment_df['문의 내용'].str.replace(pattern_str, repl, regex=True)
    payment_df['응답'] = payment_df['응답'].str.replace(pattern_str, repl, regex=True)

# 치환되지 않은 Placeholder 추출 (디스코드 공유용)
unmapped_placeholders = set()
def extract_placeholders(text):
    return re.findall(r'\{\{.*?\}\}', str(text))

payment_df['문의 내용'].apply(lambda x: unmapped_placeholders.update(extract_placeholders(x)))
payment_df['응답'].apply(lambda x: unmapped_placeholders.update(extract_placeholders(x)))

with open('payment_unmapped_placeholders.txt', 'w', encoding='utf-8') as f:
    for p in sorted(list(unmapped_placeholders)):
        f.write(f"{p}\n")

# 6. 복합/오류 문의 (100건 이하) 검토용 파일로 분리
intent_counts = payment_df['의도'].value_counts()
low_count_intents = intent_counts[intent_counts <= 100].index.tolist()

if low_count_intents:
    review_df = payment_df[payment_df['의도'].isin(low_count_intents)]
    # 검토용 파일로 따로 저장
    review_df.to_csv('payment_review_needed.csv', index=False, encoding='utf-8-sig')
    # 본 데이터에서는 제외
    payment_df = payment_df[~payment_df['의도'].isin(low_count_intents)]
    print(f"🔍 검토 필요: 100건 이하 데이터 {len(review_df)}건을 'payment_review_needed.csv'로 분리했습니다.")
else:
    print("✅ 통과: 현재 100건 이하인 복합/오류 의도(Intent)가 없습니다.")

# 6. 결과 저장
payment_df.to_csv('payment_data_ko_preprocessed.csv', index=False, encoding='utf-8-sig')
print(f"전처리 완료: {len(payment_df)}건의 데이터가 payment_data_ko_preprocessed.csv로 저장되었습니다.")
print("매핑되지 않은 Placeholder 목록은 payment_unmapped_placeholders.txt를 확인하십시오.")