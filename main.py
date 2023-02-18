from fastapi import FastAPI
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


@app.post('/create_notes')
async def create_notes(transcript: TranscriptionModel ):
    
    print("data: ", transcript)
    video_url = transcript.video_url
    user_id = str(transcript.user_id)
    chapter_name = str(transcript.chapter_name)
    subject_name = str(transcript.subject_name)


    transcription,title = get_transcription(video_url)
    chunks = get_chunks(transcription['text'])

    summarries = []

    for para in chunks:
        summary = get_summary(para)
        summarries.append(summary)    
    obj = {'title':str(title),'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name, 'video_url': video_url }
    Transcriptions.insert_one(obj)
    obj['_id'] = str(obj['_id']) 
    return obj


@app.get('/recommend_videos')
async def get_recommended_videos(data: userDataModel):
    try:
        user_id = data['user_id']
        obj = Transcriptions.find({'user_id': user_id},{"chunks":1})
        obj = list(obj)
        # print(obj)
        merged = []
        for i in range(len(obj)):
            obj[i]['_id'] = str(obj[i]['_id'])
            temp = ""
            for chunk in obj[i]['chunks']:
                temp = temp + chunk
            merged.append(temp)

        recom = get_recommendations(merged)
        print(recom)
        return {"recommendations":recom}, 200
    
    except Exception as e:
        return {'message': 'Server Error' + str(e)}, 500
