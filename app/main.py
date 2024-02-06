from fastapi import FastAPI, status
import uvicorn
import stanza
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSeq2SeqLM




stanza.download('en')
nlp = stanza.Pipeline('en')


tags_dict = {
    "ADV":"قید حالت",
    "ADJ":"صفت",
    "INTJ":"حرف یا کلمه ندا (برای بیان احساسات و خطاب قرار دادن یا صدا زدن کسی یا چیزی)",
    "NOUN":"اسم",
    "PROPN":"اسم خاص",
    "VERB":"فعل",
    "ADP":"قید زمان یا مکان",
    "AUX":"فعل کمکی",
    "CCONJ":"حروف یا کلمات ربطی",
    "DET":"حروف یا کلمات اشاره",
    "NUM":"تعداد",
    "PART":"حروف اضافه",
    "PRON":"ضمیر",
    "SCONJ":"حروف یا کلمات ربطی شرطی",
    "PUNCT":"",
    "SYM":"",
    "X":""
}


# model_size = "base"

# model_name = f"persiannlp/mt5-{model_size}-parsinlu-translation_en_fa"
# tokenizer = MT5Tokenizer.from_pretrained(model_name)
# model = MT5ForConditionalGeneration.from_pretrained(model_name)

tokenizer = AutoTokenizer.from_pretrained("quantized_model_translator", use_cache=False)
model = ORTModelForSeq2SeqLM.from_pretrained("quantized_model_translator", use_cache=False)

def run_model(input_string, **generator_args):
    inputs = tokenizer(input_string, return_tensors="pt")
    res = model.generate(**inputs, **generator_args)
    output = tokenizer.batch_decode(res, skip_special_tokens=True)
    
    return output

def analyse(org_doc:str):
    
    doc = nlp(org_doc)
    
    final_doc = {"words_list":[]}
    
    for sent in doc.sentences:
        for word in sent.words:
            if word.upos not in ["PUNCT", "X", "SYM"]:
                temp_dict = {
                    "word":"",
                    "lemmatized":"",
                    "meaning":"",
                    "lemmatized_meaning":"",
                    "upos_tag":"",
                    "number":"",
                }
                temp_dict["word"] = word.text
                temp_dict["lemmatized"] = word.lemma
                temp_dict["meaning"] = run_model(word.text)
                temp_dict["lemmatized_meaning"] = run_model(word.lemma)
                temp_dict["upos_tag"] = tags_dict[word.upos]
                if word.feats:
                    if "Number" in word.feats:
                        number = word.feats.split("=")[-1]
                        if number == "Sing":
                            temp_dict["number"] = "مفرد"
                        elif number == "Plur":
                            temp_dict["number"] = "جمع"
                final_doc["words_list"].append(temp_dict)

    gen_params = {"max_new_tokens":128, "top_k":30, "top_p":0.95, "no_repeat_ngram_size":2}
    sentence_meaning = run_model(org_doc.strip(), **gen_params)
    final_doc["sent_meaning"] = sentence_meaning
    return final_doc




app = FastAPI()

@app.get("/translate/{phrase}", status_code=status.HTTP_200_OK)
async def translate(phrase:str):
    phrase = phrase.strip(" ")
    res =  analyse(phrase)
    return {"translate": res}


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8090)

