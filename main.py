# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uvicorn

# 1. Swagger 문서 설정 (제목, 설명)
app = FastAPI(
    title="PetLog Health API",
    description="외부 스마트 청진기(Withapet) 데이터 수신용 서버",
    version="1.0.0"
)

# 2. 데이터 모델 정의 (Spring의 DTO 역할)
# 이렇게 클래스로 정의하면 Swagger에 자동으로 명세서가 그려집니다.

class PetInfo(BaseModel):
    name: str = Field(..., example="복실이", description="반려동물 이름")
    type: str = Field(..., example="DOG", description="동물 종류")
    birth: str = Field(..., example="2025-08-13", description="생년월일")
    breed: str = Field(..., example="Maltipoo", description="품종")
    gender: str = Field(..., example="MALE", description="성별")

class Analysis(BaseModel):
    result: str = Field(..., example="WARNING", description="심장 분석 결과")
    abnormal_probability: int = Field(..., example=68, description="비정상 확률(%)")
    mmvd_stage: str = Field(..., example="B1", description="MMVD 단계")

class Vitals(BaseModel):
    bpm: int = Field(..., example=72, description="심박수")
    weight: float = Field(..., example=1.0, description="체중(kg)")
    bcs: int = Field(..., example=3, description="신체충실지수(1~5)")
    respiration_rate: int = Field(..., example=20, description="분당 호흡수")

class Survey(BaseModel):
    vitality: Optional[int] = Field(None, description="활력 점수")
    appetite: Optional[int] = Field(None, description="식욕 점수")
    cough: Optional[int] = Field(None, description="기침 빈도")

# 전체를 감싸는 메인 DTO
class HealthDataPayload(BaseModel):
    pet_info: PetInfo
    analysis: Analysis
    vitals: Vitals
    survey: Optional[Survey] = None

# 3. API 엔드포인트
@app.post("/api/v1/webhook/health-data", summary="건강 데이터 수신", tags=["Webhook"])
async def receive_health_data(data: HealthDataPayload):
    """
    외부 업체로부터 전송되는 JSON 데이터를 수신합니다.
    - 자동으로 JSON 파싱 및 유효성 검사가 수행됩니다.
    - 데이터가 누락되거나 타입이 틀리면 422 에러를 반환합니다.
    """
    try:
        # 로그 출력 (객체를 dict로 변환)
        print(f"\n[수신 로그 - {datetime.now()}] 데이터 도착!")
        print("="*50)
        print(data.model_dump_json(indent=2)) # 보기 좋게 JSON 출력
        print("="*50)

        # TODO: 여기서 DB 저장 로직 수행 (data.pet_info.name 처럼 접근 가능)
        
        return {
            "status": "success",
            "message": "Data received successfully",
            "received_pet": data.pet_info.name
        }

    except Exception as e:
        print(f"!! 서버 에러: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)