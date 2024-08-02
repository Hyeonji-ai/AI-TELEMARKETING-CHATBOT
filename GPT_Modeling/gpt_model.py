import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import PreTrainedTokenizerFast, GPT2LMHeadModel
import re
device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = torch.device("cuda")

BOS = "</s>"
EOS = "</s>"
PAD = "<pad>"
MASK = "<unused0>"
U_TKN='<usr>'
S_TKN='<sys>'
SENT='<unused1>'


koGPT2_TOKENIZER = PreTrainedTokenizerFast.from_pretrained("skt/kogpt2-base-v2", bos_token=BOS, eos_token=EOS, unk_token="<unk>", pad_token=PAD, mask_token=MASK,)
model = GPT2LMHeadModel.from_pretrained('skt/kogpt2-base-v2')



class KoGPTChatbotDataset(Dataset):
    def __init__(self, chats, max_len=50):  
        self._data = chats
        self.max_len = max_len
        self.q_token = U_TKN
        self.a_token = S_TKN
        self.sent_token = SENT
        self.eos = EOS
        self.mask = MASK
        self.tokenizer = koGPT2_TOKENIZER

    def __len__(self):  
        return len(self._data)

    def __getitem__(self, idx): 
        turn = self._data.iloc[idx]
        q = turn["Q"] 
        q = re.sub(r"([?.!,])", r" ", str(q)) 

        a = turn["A"] 
        a = re.sub(r"([?.!,])", r" ", str(a))  

        q_toked = self.tokenizer.tokenize(self.q_token + q + self.sent_token)
        q_len = len(q_toked)

        a_toked = self.tokenizer.tokenize(self.a_token + a + self.eos)
        a_len = len(a_toked)

        if q_len > self.max_len:
            a_len = self.max_len - q_len        
            if a_len <= 0:    
                q_toked = q_toked[-(int(self.max_len / 2)) :]   
                q_len = len(q_toked)
                a_len = self.max_len - q_len           
            a_toked = a_toked[:a_len]
            a_len = len(a_toked)


        if q_len + a_len > self.max_len:
            a_len = self.max_len - q_len 
            if a_len <= 0:      
                q_toked = q_toked[-(int(self.max_len / 2)) :] 
                q_len = len(q_toked)
                a_len = self.max_len - q_len  
            a_toked = a_toked[:a_len]
            a_len = len(a_toked)

        labels = [self.mask,] * q_len + a_toked[1:]
        mask = [0] * q_len + [1] * a_len + [0] * (self.max_len - q_len - a_len)
        labels_ids = self.tokenizer.convert_tokens_to_ids(labels)

        while len(labels_ids) < self.max_len:
            labels_ids += [self.tokenizer.pad_token_id]

    
        token_ids = self.tokenizer.convert_tokens_to_ids(q_toked + a_toked)

        while len(token_ids) < self.max_len:
            token_ids += [self.tokenizer.pad_token_id]

        return (token_ids, mask, labels_ids)

class KoGPT_Main():
    def __init__(self):
        self.q = ""
        self.a = ""

    def collate_batch(batch):
        data = [item[0] for item in batch]
        mask = [item[1] for item in batch]
        label = [item[2] for item in batch]
        return torch.LongTensor(data), torch.LongTensor(mask), torch.LongTensor(label)

    def call_kogpt(self, text):
        
        data = pd.read_csv('GPT_Modeling/gpt_dataset.csv')
        data = data.drop(columns=['Unnamed: 0'])
        data = data[~data['counselor'].isna()]

        model = torch.load('GPT_Modeling/chatbot_model.pt')

        sent ="0"
        with torch.no_grad():
            model.eval()
            # f = open("dialog/user_input.txt", 'r')
            data = text
            # f.close()
            q = data
            a = ""
            while 1:
                input_ids = torch.LongTensor(koGPT2_TOKENIZER.encode(U_TKN + q + SENT+ sent + S_TKN + a))
                pred = model(input_ids)
                pred = pred.logits
                gen = koGPT2_TOKENIZER.convert_ids_to_tokens(torch.argmax(pred, dim=-1).squeeze().numpy().tolist())[-1]
                if gen == EOS:
                    break
                a += gen.replace("▁", " ")
            answer=a.strip()

        return answer
            # f= open('dialog/coun1.txt','w')
            # f.write(a.strip())
            # f.close()
                
