from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
        self.db = self.client.prompt_optimizer
        self.prompts = self.db.prompts

    def _convert_objectid(self, document: Dict) -> Dict:
        """ObjectId'yi string'e dönüştür"""
        if document and "_id" in document:
            document["_id"] = str(document["_id"])
        return document

    async def create_prompt(self, prompt_data: Dict) -> str:
        """Yeni bir prompt kaydı oluştur"""
        result = await self.prompts.insert_one(prompt_data)
        return str(result.inserted_id)

    async def get_prompt(self, prompt_id: str) -> Optional[Dict]:
        """Prompt ID'ye göre kayıt getir"""
        try:
            result = await self.prompts.find_one({"_id": ObjectId(prompt_id)})
            return self._convert_objectid(result) if result else None
        except:
            return None

    async def update_prompt(self, prompt_id: str, update_data: Dict) -> bool:
        """Prompt kaydını güncelle"""
        try:
            result = await self.prompts.update_one(
                {"_id": ObjectId(prompt_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False

    async def add_model_response(self, prompt_id: str, response_data: Dict) -> bool:
        """Prompt kaydına yeni bir model yanıtı ekle"""
        try:
            result = await self.prompts.update_one(
                {"_id": ObjectId(prompt_id)},
                {"$push": {"model_responses": response_data}}
            )
            return result.modified_count > 0
        except:
            return False

    async def get_prompt_metrics(self, prompt_id: str) -> Dict:
        """Prompt için metrik ve istatistikleri getir"""
        prompt = await self.get_prompt(prompt_id)
        if not prompt:
            return {}

        total_tokens = 0
        total_cost = 0
        iterations = len(prompt.get("model_responses", []))

        for response in prompt.get("model_responses", []):
            total_tokens += response.get("total_tokens", 0)
            total_cost += response.get("cost_usd", 0)

        return {
            "prompt_id": str(prompt["_id"]),
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "iterations": iterations,
            "original_prompt_length": len(prompt.get("original_prompt", "").split()),
            "optimized_prompt_length": len(prompt.get("optimized_prompt", "").split()) if prompt.get("optimized_prompt") else None
        } 