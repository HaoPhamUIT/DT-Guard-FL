import json
with open('/Users/hao.pham/PycharmProjects/DTGuardFL/DT-Guard-FL/results/generic/exp5_dtpw.json') as f:
    d = json.load(f)
print('Keys:', list(d.keys()))
print('Config:', json.dumps(d.get('config',{}), indent=2))

print('\nFinal Accuracy:')
for k,v in d['accuracy'].items():
    val = list(v.values())[0]
    print(f'  {k}: {val*100:.2f}%')

if 'score_history' in d:
    print('\nScore history strategies:', list(d['score_history'].keys()))
    for k in d['score_history']:
        for atk in d['score_history'][k]:
            arr = d['score_history'][k][atk]
            print(f'  {k}/{atk}: {len(arr)} rounds x {len(arr[0]) if arr else 0} clients')
            if arr:
                last = arr[-1]
                fr_w = [last[i] for i in [16,17,18,19]]
                norm_w = [last[i] for i in range(16)]
                print(f'    Last round: normal_avg={sum(norm_w)/len(norm_w):.4f}  fr_avg={sum(fr_w)/len(fr_w):.4f}')

