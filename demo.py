import openai
import os

openai.organization = 'org-05OhvLUEsq7HBkTvP2PVLKbx'

openai.api_key = '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'
model_list = openai.Model.list()
print(model_list)
