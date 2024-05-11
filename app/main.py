from cv2 import sort
from fastapi import FastAPI, status
import uvicorn
import stanza
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSeq2SeqLM
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import string


stanza.download('en')
nlp = stanza.Pipeline('en')

en_letters = list(string.ascii_lowercase) + list(string.ascii_uppercase)

fa_stopwords = ["ـ", ":", "،", "؛",
                ".", "+", "=", "-",
                "*", "(", ")", "/",
                "[", "]", "^", "$", 
                "!", "<", ">", "<<", ">>"]



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
    processed_outs = []
    for out in output:
        for sw in fa_stopwords:
            if sw in out:
                out = out.replace(sw, "")
        if "ي" in out:
            out = out.replace("ي", "ی")
            
        out = out.strip()
        processed_outs.append(out)
    return processed_outs



def sort_w_trans(sent_trans:str, word_trans_list:list[str]):
    for sw in fa_stopwords:
        if sw in sent_trans:
            sent_trans = sent_trans.replace(sw, "")
    
    word_trans_list = list(set([wt.strip().strip("،").strip(".").strip(":") for wt in word_trans_list]))
    sent_trans = sent_trans.strip()
    word_trans_list.append(sent_trans)
    tfidf = TfidfVectorizer().fit_transform(word_trans_list)
    
    pairwise_similarity = tfidf * tfidf.T
    
    sims_vec = pairwise_similarity.toarray()[:,-1]
    sims_vec = sims_vec[:-1].tolist()
    scores_dict = [
        {"word":w, "score":w_score} for w , w_score in zip(word_trans_list[:-1], sims_vec)
    ]
    
    sorted_dicts = sorted(
        scores_dict, key=lambda x : x["score"], reverse=True
    )
    
    sorted_words = [w_info["word"].strip() for w_info in sorted_dicts]

    sorted_words = [finalw.strip(".").strip("،") for finalw in sorted_words]
    return sorted_words
    
    
    
    
def remove_en_letters(ws_trans:list[str]):
    
    for wtemp in ws_trans:
        
        for en_letter in en_letters:
            if en_letter in wtemp:
                ws_trans.remove(wtemp)
                break
    
    return ws_trans
        

def analyse(org_doc:str):
    
    sent_gen_params = {
        "max_new_tokens":128,
        "no_repeat_ngram_size":2,
        }
    sentence_meaning = run_model(org_doc.strip(), **sent_gen_params)
    
    word_gen_args = {
        "max_new_tokens":40,
        "top_k":30,
        "top_p":0.98,
        "no_repeat_ngram_size":2,
        "num_beams":10,
        "num_return_sequences":10,
        "do_sample":True,
        "early_stopping":True
                  }
    
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
                temp_dict["meaning"] = list(set(run_model(word.text, **word_gen_args)))
                temp_dict["lemmatized_meaning"] = list(set(run_model(word.lemma, **word_gen_args)))
                
                temp_dict["meaning"] = remove_en_letters(
                    sort_w_trans(
                        sentence_meaning[0], temp_dict["meaning"]
                        )
                    )
                
                temp_dict["lemmatized_meaning"] = remove_en_letters(
                    sort_w_trans(
                        sentence_meaning[0], temp_dict["lemmatized_meaning"]
                        )
                )
                    
                                                   
                
                temp_dict["upos_tag"] = tags_dict[word.upos]
                if word.feats:
                    if "Number" in word.feats:
                        number = word.feats.split("=")[-1]
                        if number == "Sing":
                            temp_dict["number"] = "مفرد"
                        elif number == "Plur":
                            temp_dict["number"] = "جمع"
                final_doc["words_list"].append(temp_dict)

    
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

