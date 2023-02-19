from fastapi import FastAPI
import uvicorn
import motor.motor_asyncio
from utilities import get_transcription,get_chunks,get_summary, get_recommendations
from models import *

app = FastAPI()

MONGO_DETAILS = "mongodb+srv://admin:12345@cluster0.crod9kz.mongodb.net/?retryWrites=true&w=majority"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.hackathon
Transcriptions = database.get_collection("Transcriptions")


@app.get('/')
def index():
    return {'message':"Hello World"}


@app.post('/get_transcription')
async def get_transcription(transcript: TranscriptionModel ):
    try:
        video_url = transcript.video_url
        user_id = str(transcript.user_id)
        chapter_name = str(transcript.chapter_name)
        subject_name = str(transcript.subject_name)


        transcription,title = get_transcription(video_url)
        chunks = get_chunks(transcription['text'])
        print(type(transcription['text']))

        summarries = []

        for para in chunks:
            summary = get_summary(para)
            summarries.append(summary)    
        obj = {'title':str(title),'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name, 'video_url': video_url }
        
        await Transcriptions.insert_one(obj)
        obj['_id'] = str(obj['_id']) 
        return obj
    
    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}

@app.post("/ocr_to_notes")
async def ocr_to_notes(data: OCRToNotesModel):
    try:
        print(data)
        user_id = str(data.user_id)
        chapter_name = str(data.chapter_name)
        subject_name = str(data.subject_name)
        text = str(data.text)

        chunks = get_chunks(text)
        summarries = []

        for para in chunks:
            summary = get_summary(para)
            summarries.append(summary)    
        obj = {'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name }
        
        await Transcriptions.insert_one(obj)
        obj['_id'] = str(obj['_id']) 
        return obj

    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}


@app.get('/recommend_videos')
async def get_recommended_videos(data: userDataModel):
    try:
        user_id = data.user_id
        obj = Transcriptions.find({'user_id': user_id},{"chunks":1})

        obj = await obj.to_list(length=100)
        
        merged = []
        for i in range(len(obj)):
            obj[i]['_id'] = str(obj[i]['_id'])
            temp = ""
            for chunk in obj[i]['chunks']:
                temp = temp + chunk
            merged.append(temp)

        recom = get_recommendations(merged)
        print(recom)
        return {"recommendations":recom}
    
    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}

