"""Small, bundled workflow helper. This is a rule-based fallback, not an LLM."""
import re

TEXT = {
'en': {
'hello': 'Hello! I can help prepare a consultation, organize symptoms, explain report-review steps, and navigate SAHAYAJ. Ask a specific question. For open-ended AI conversation, download the local Ollama model once.',
'urgent': 'Your message mentions a potentially urgent symptom. Please seek immediate in-person medical assistance rather than waiting for this chat. I cannot assess severity or rule out an emergency.',
'medicine': 'I cannot select a medicine, remedy, dose, or change your treatment. Tell your clinician your symptoms, current medicines and supplements, allergies, and relevant history. Do not stop prescribed treatment based on this helper.',
'report': 'Open a consultation, choose a PDF/JPG/PNG medical report, and select Upload report. Extracted values are unverified until the assigned doctor checks the original document. The doctor can accept, correct or reject findings. A number alone does not establish a diagnosis.',
'visit': 'To start: choose New visit, select the medical branch, describe your main problem and duration, enter age and discomfort, then complete routines and health background. Include medicines and allergies. Submit for review; reports can be uploaded afterwards.',
'branch': 'Choose the branch your clinic offers: modern medicine/allopathy, Ayurveda, Homeopathy, Unani, Siddha, Naturopathy/yoga, Dental or Other. Choose General / unsure if uncertain. A registered clinician in that branch must be available. Workflow support does not imply that every treatment has equal scientific evidence.',
'language': 'Use the language selector for English, Hindi or Punjabi core controls. Typed records retain their original text. Dictate and Read aloud depend on your browser and installed voices; browser dictation can require internet.',
'symptom': 'For your consultation, record when the problem started, its location, changes over time, severity, associated symptoms, measured observations if available, current medicines and allergies. A qualified clinician must assess the cause; this helper cannot diagnose it.',
'doctor': 'Consultation review checklist: clarify onset and progression, associated symptoms, relevant history, medicines and allergies; verify original reports and units; review flagged symptoms and missing information. Decide within your professional scope. AI suggestions do not update or finalize the record.',
'unknown': 'This bundled offline helper has limited knowledge and cannot answer that question reliably. I can help with visit preparation, reports, branches, language controls and review checklists. For broader answers, install Ollama and download the model using setup-offline.cmd. No paid API key is needed.',
'limit': 'Basic offline helper — fixed guidance, not a diagnosis or prescription.'
},
'hi': {
'hello': 'नमस्ते! मैं परामर्श की तैयारी, लक्षणों के विवरण, रिपोर्ट की समीक्षा और SAHAYAJ के उपयोग में मदद कर सकता हूँ। खुली बातचीत के लिए Ollama का local model एक बार डाउनलोड करें।',
'urgent': 'आपके संदेश में संभावित गंभीर लक्षण का उल्लेख है। इस चैट का इंतज़ार करने के बजाय तुरंत प्रत्यक्ष चिकित्सा सहायता लें। मैं गंभीरता का आकलन या आपात स्थिति को खारिज नहीं कर सकता।',
'medicine': 'मैं दवा, उपचार या खुराक नहीं चुन सकता और इलाज बदलने की सलाह नहीं देता। डॉक्टर को लक्षण, वर्तमान दवाइयाँ, सप्लीमेंट, एलर्जी और इतिहास बताएँ। इस सहायक के आधार पर निर्धारित इलाज बंद न करें।',
'report': 'परामर्श खोलें, PDF/JPG/PNG रिपोर्ट चुनें और Upload report दबाएँ। डॉक्टर मूल दस्तावेज़ देखकर निकाले गए मान स्वीकार, सुधार या अस्वीकार करेगा। केवल एक संख्या से निदान नहीं होता।',
'visit': 'New visit चुनें, चिकित्सा पद्धति, मुख्य समस्या, अवधि, आयु और तकलीफ़ भरें। फिर आदतें, स्वास्थ्य इतिहास, दवाइयाँ और एलर्जी बताएँ। समीक्षा के लिए जमा करने के बाद रिपोर्ट अपलोड कर सकते हैं।',
'branch': 'अपनी क्लिनिक की उपलब्ध चिकित्सा पद्धति चुनें: आधुनिक चिकित्सा, आयुर्वेद, होम्योपैथी, यूनानी, सिद्ध, प्राकृतिक चिकित्सा/योग, दंत या अन्य। अनिश्चित हों तो General / unsure चुनें। उस शाखा का डॉक्टर उपलब्ध होना चाहिए। सभी उपचारों के प्रमाण समान नहीं हैं।',
'language': 'ऊपर के भाषा विकल्प से English, हिन्दी या ਪੰਜਾਬੀ चुनें। मूल चिकित्सा विवरण नहीं बदलते। बोलकर लिखना और सुनना browser तथा उपलब्ध आवाज़ों पर निर्भर हैं; browser dictation में internet लग सकता है।',
'symptom': 'डॉक्टर के लिए लिखें: समस्या कब शुरू हुई, कहाँ है, कैसे बदली, कितनी तकलीफ़ है, साथ के लक्षण, मापी गई जानकारी, दवाइयाँ और एलर्जी। कारण का आकलन योग्य डॉक्टर करेगा; यह सहायक निदान नहीं कर सकता।',
'doctor': 'समीक्षा सूची: शुरुआत और बदलाव, साथ के लक्षण, पुराना इतिहास, दवाइयाँ और एलर्जी स्पष्ट करें। मूल रिपोर्ट और units जाँचें। चेतावनियों और अधूरी जानकारी की समीक्षा करें। अपने पेशेवर दायरे में निर्णय लें। AI से रिकॉर्ड अपने-आप नहीं बदलता।',
'unknown': 'इस basic offline helper की जानकारी सीमित है; मैं इसका भरोसेमंद उत्तर नहीं दे सकता। मैं परामर्श की तैयारी, रिपोर्ट, शाखा और समीक्षा सूची में मदद करता हूँ। विस्तृत जवाबों के लिए setup-offline.cmd से Ollama model डाउनलोड करें। Paid API key नहीं चाहिए।',
'limit': 'Basic offline helper — सीमित मार्गदर्शन; निदान या prescription नहीं।'
},
'pa': {
'hello': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਸਲਾਹ ਦੀ ਤਿਆਰੀ, ਲੱਛਣਾਂ ਦੇ ਵੇਰਵੇ, ਰਿਪੋਰਟ ਸਮੀਖਿਆ ਅਤੇ SAHAYAJ ਵਰਤਣ ਵਿੱਚ ਮਦਦ ਕਰ ਸਕਦਾ ਹਾਂ। ਖੁੱਲ੍ਹੀ ਗੱਲਬਾਤ ਲਈ Ollama ਦਾ local model ਇੱਕ ਵਾਰ ਡਾਊਨਲੋਡ ਕਰੋ।',
'urgent': 'ਤੁਹਾਡੇ ਸੁਨੇਹੇ ਵਿੱਚ ਸੰਭਾਵੀ ਗੰਭੀਰ ਲੱਛਣ ਦਾ ਜ਼ਿਕਰ ਹੈ। ਇਸ ਚੈਟ ਦੀ ਉਡੀਕ ਕਰਨ ਦੀ ਬਜਾਏ ਤੁਰੰਤ ਡਾਕਟਰੀ ਮਦਦ ਲਵੋ। ਮੈਂ ਗੰਭੀਰਤਾ ਨਹੀਂ ਜਾਂਚ ਸਕਦਾ ਜਾਂ ਐਮਰਜੈਂਸੀ ਨੂੰ ਰੱਦ ਨਹੀਂ ਕਰ ਸਕਦਾ।',
'medicine': 'ਮੈਂ ਦਵਾਈ, ਇਲਾਜ ਜਾਂ ਖੁਰਾਕ ਨਹੀਂ ਚੁਣ ਸਕਦਾ। ਡਾਕਟਰ ਨੂੰ ਲੱਛਣ, ਮੌਜੂਦਾ ਦਵਾਈਆਂ, ਸਪਲੀਮੈਂਟ, ਐਲਰਜੀਆਂ ਅਤੇ ਪੁਰਾਣਾ ਇਤਿਹਾਸ ਦੱਸੋ। ਇਸ ਸਹਾਇਕ ਦੇ ਆਧਾਰ ਤੇ ਨਿਰਧਾਰਤ ਇਲਾਜ ਬੰਦ ਨਾ ਕਰੋ।',
'report': 'ਸਲਾਹ ਖੋਲ੍ਹੋ, PDF/JPG/PNG ਰਿਪੋਰਟ ਚੁਣੋ ਅਤੇ Upload report ਦਬਾਓ। ਡਾਕਟਰ ਅਸਲ ਦਸਤਾਵੇਜ਼ ਵੇਖ ਕੇ ਕੱਢੇ ਮੁੱਲ ਸਵੀਕਾਰ, ਠੀਕ ਜਾਂ ਰੱਦ ਕਰੇਗਾ। ਇਕੱਲੀ ਗਿਣਤੀ ਨਾਲ ਨਿਦਾਨ ਨਹੀਂ ਹੁੰਦਾ।',
'visit': 'New visit ਚੁਣੋ। ਇਲਾਜ ਦੀ ਸ਼ਾਖਾ, ਮੁੱਖ ਸਮੱਸਿਆ, ਸਮਾਂ, ਉਮਰ ਅਤੇ ਤਕਲੀਫ਼ ਭਰੋ। ਫਿਰ ਆਦਤਾਂ, ਸਿਹਤ ਦਾ ਇਤਿਹਾਸ, ਦਵਾਈਆਂ ਅਤੇ ਐਲਰਜੀਆਂ ਦੱਸੋ। ਜਮ੍ਹਾਂ ਕਰਨ ਤੋਂ ਬਾਅਦ ਰਿਪੋਰਟ ਪਾ ਸਕਦੇ ਹੋ।',
'branch': 'ਆਪਣੀ ਕਲੀਨਿਕ ਦੀ ਉਪਲਬਧ ਸ਼ਾਖਾ ਚੁਣੋ: ਆਧੁਨਿਕ ਮੈਡੀਸਿਨ, ਆਯੁਰਵੇਦ, ਹੋਮਿਓਪੈਥੀ, ਯੂਨਾਨੀ, ਸਿੱਧਾ, ਕੁਦਰਤੀ ਇਲਾਜ/ਯੋਗ, ਦੰਦਾਂ ਦਾ ਇਲਾਜ ਜਾਂ ਹੋਰ। ਪਤਾ ਨਾ ਹੋਵੇ ਤਾਂ General / unsure ਚੁਣੋ। ਉਸ ਸ਼ਾਖਾ ਦਾ ਡਾਕਟਰ ਉਪਲਬਧ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ। ਹਰ ਇਲਾਜ ਦੇ ਸਬੂਤ ਬਰਾਬਰ ਨਹੀਂ ਹੁੰਦੇ।',
'language': 'ਭਾਸ਼ਾ ਚੋਣ ਤੋਂ English, हिन्दी ਜਾਂ ਪੰਜਾਬੀ ਚੁਣੋ। ਅਸਲ ਡਾਕਟਰੀ ਵੇਰਵੇ ਨਹੀਂ ਬਦਲਦੇ। ਬੋਲ ਕੇ ਲਿਖਣਾ ਅਤੇ ਸੁਣਨਾ browser ਤੇ ਆਵਾਜ਼ਾਂ ਉੱਤੇ ਨਿਰਭਰ ਹੈ; browser dictation ਲਈ internet ਲੱਗ ਸਕਦਾ ਹੈ।',
'symptom': 'ਡਾਕਟਰ ਲਈ ਲਿਖੋ: ਸਮੱਸਿਆ ਕਦੋਂ ਸ਼ੁਰੂ ਹੋਈ, ਕਿੱਥੇ ਹੈ, ਕਿਵੇਂ ਬਦਲੀ, ਕਿੰਨੀ ਤਕਲੀਫ਼ ਹੈ, ਹੋਰ ਲੱਛਣ, ਮਾਪੀ ਜਾਣਕਾਰੀ, ਦਵਾਈਆਂ ਅਤੇ ਐਲਰਜੀਆਂ। ਕਾਰਨ ਦਾ ਮੁਲਾਂਕਣ ਯੋਗ ਡਾਕਟਰ ਕਰੇਗਾ; ਇਹ ਸਹਾਇਕ ਨਿਦਾਨ ਨਹੀਂ ਕਰ ਸਕਦਾ।',
'doctor': 'ਸਮੀਖਿਆ ਸੂਚੀ: ਸ਼ੁਰੂਆਤ ਅਤੇ ਬਦਲਾਅ, ਨਾਲ ਦੇ ਲੱਛਣ, ਇਤਿਹਾਸ, ਦਵਾਈਆਂ ਅਤੇ ਐਲਰਜੀਆਂ ਸਪਸ਼ਟ ਕਰੋ। ਅਸਲ ਰਿਪੋਰਟਾਂ ਅਤੇ units ਜਾਂਚੋ। ਚੇਤਾਵਨੀਆਂ ਅਤੇ ਅਧੂਰੀ ਜਾਣਕਾਰੀ ਦੀ ਸਮੀਖਿਆ ਕਰੋ। ਆਪਣੇ ਪੇਸ਼ੇਵਰ ਦਾਇਰੇ ਵਿੱਚ ਫੈਸਲਾ ਲਵੋ। AI ਰਿਕਾਰਡ ਆਪਣੇ ਆਪ ਨਹੀਂ ਬਦਲਦਾ।',
'unknown': 'ਇਸ basic offline helper ਦੀ ਜਾਣਕਾਰੀ ਸੀਮਿਤ ਹੈ; ਮੈਂ ਇਸ ਦਾ ਭਰੋਸੇਯੋਗ ਜਵਾਬ ਨਹੀਂ ਦੇ ਸਕਦਾ। ਵੱਡੇ ਸਵਾਲਾਂ ਲਈ setup-offline.cmd ਨਾਲ Ollama model ਡਾਊਨਲੋਡ ਕਰੋ। Paid API key ਦੀ ਲੋੜ ਨਹੀਂ।',
'limit': 'Basic offline helper — ਸੀਮਿਤ ਜਾਣਕਾਰੀ; ਨਿਦਾਨ ਜਾਂ prescription ਨਹੀਂ।'
}}
URGENT = ('chest pain','difficulty breathing','cannot breathe','severe bleeding','unconscious','सीने में दर्द','सांस नहीं','साँस नहीं','बेहोश','ਛਾਤੀ ਦਰਦ','ਸਾਹ ਨਹੀਂ','ਬੇਹੋਸ਼')
def urgent_message(text): return any(word in text.lower() for word in URGENT)
def basic_reply(role, language, messages, context):
    lang=language if language in TEXT else 'en'; t=TEXT[lang]
    text=messages[-1]['content'].lower()
    if urgent_message(text): key='urgent'
    elif any(w in text for w in ['medicine','dose','prescri','remedy','tablet','दवा','खुराक','ਦਵਾਈ','ਖੁਰਾਕ']): key='medicine'
    elif any(w in text for w in ['report','pdf','blood test','रिपोर्ट','ਰਿਪੋਰਟ']): key='report'
    elif any(w in text for w in ['branch','ayurved','homeopath','allopath','पद्धति','शाखा','ਆਯੁਰਵੇਦ','ਸ਼ਾਖਾ']): key='branch'
    elif any(w in text for w in ['language','voice','dictat','भाषा','ਬੋਲੀ','ਭਾਸ਼ਾ']): key='language'
    elif any(w in text for w in ['appointment','new visit','start','consultation','परामर्श','शुरू','ਸਲਾਹ','ਸ਼ੁਰੂ']): key='visit'
    elif any(w in text for w in ['fever','cough','pain','symptom','दर्द','बुखार','लक्षण','ਦਰਦ','ਬੁਖਾਰ','ਲੱਛਣ']): key='symptom'
    elif re.search(r'\b(hello|hi|hey|help)\b',text) or any(w in text for w in ['नमस्ते','ਸਤ ਸ੍ਰੀ']): key='hello'
    elif role=='doctor' and any(w in text for w in ['review','checklist','missing','clarify','समीक्षा','ਸਮੀਖਿਆ']): key='doctor'
    else: key='unknown'
    if role=='doctor' and context and key not in ['urgent','medicine']:
        # Original patient text is not repeated or interpreted as diagnosis.
        return t['doctor']+'\n\n'+t['limit']
    return t[key]+'\n\n'+t['limit']
