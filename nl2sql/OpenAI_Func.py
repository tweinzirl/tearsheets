# OpenAI_Func.py
# General purpose OpenAI functions
import openai
import tiktoken

# count the number of input tokens in prompt
def Num_Tokens_From_String(Prompt: str, Encoding_Base=None, Verbose=False) -> int:
    """Returns the number of tokens in a text string."""
    if Encoding_Base is not None:
        try:
           encoding = tiktoken.get_encoding(Encoding_Base)
        except:
            print(f'tiktoken.get_encoding failed')
            return -1
    else:
        print(f'Num_Tokens_From_String: Missing Encoding Base {Encoding_Base}')
        return -1
    
    num_tokens = len(encoding.encode(Prompt))
    if Verbose:
        print(f'number of tokens {num_tokens}')
    return num_tokens

##############################################################################
# Encoding/Decoding
def Encoding(Txt, Encoding_Base, Verbose=False):
    encoding = tiktoken.get_encoding(Encoding_Base)
    Encodings = encoding.encode(Txt)
    if Verbose:
        print(f'Encodings:  {Encodings}')
    return Encodings

def Decoding(Txt, Encodings, Encoding_Base, Verbose=False):
    if not Txt:
        Txt = Encodings
    encoding = tiktoken.get_encoding(Encoding_Base)
    Decoded_txt = encoding.decode(Txt)
    if Verbose:
        print(f'Decoded text:  {Decoded_txt}')
    return Decoded_txt

 ############################################################################## 
# Extimate prompt cost per GPT model
def Prompt_Cost(Prompt, Model, Token_Cost, Encoding_Base):
    Cost = Token_Cost[Model]  # cost per 1K tokens
    Input_Cost = Cost['Input']*Num_Tokens_From_String(Prompt,Encoding_Base, Verbose=False)
    return(Input_Cost, Num_Tokens_From_String(Prompt, Encoding_Base, Verbose=False))

def OpenAI_Usage_Cost(Response, Model, Token_Cost):
        Cost = Token_Cost[Model]  # cost per 1K tokens
        Total_Cost = Cost['Input']*Response['usage']['prompt_tokens'] + \
            Cost['Output']*Response['usage']['completion_tokens']
        return(Total_Cost, Response['usage']['total_tokens'])


def OpenAI_Embeddings_Cost(Response, Token_Cost, Model):
    Cost = Token_Cost[Model]  # cost per 1K tokens
    Total_Cost = Cost['Input']*Response['usage']['total_tokens'] 
    return(Total_Cost, Response['usage']['total_tokens'])