

## 31064IEEE INTERNET OF THINGS JOURNAL, VOL. 12, NO. 15, 1 AUGUST 2025
## Enhanced Traffic Carbon Emissions Data Sharing
and Modeling via Blockchain and Personalized
Federated Learning in IIoT Ecosystem
Xinhuan Zhang, Hongjie Liu,andFanYang
Abstract—The   energy   transition   is   essential   for   achieving
sustainable  development,  and  in  this  context,  sharing  traffic
carbon emissions data within the IIoT ecosystem plays a pivotal
role  in  incentivizing  the  reduction  of  greenhouse  gas  emissions
and  promoting  cleaner  transportation  solutions.  By  leveraging
interconnected  IoT  devices  and  data  analytics,  we  can  enhance
transparency and collaboration, driving more effective strategies
for sustainable transportation. However, managing traffic carbon
emissions  and  facilitating  the  complex  sharing  of  emission  data
across  various  entities  present  significant  challenges.  To  address
these  issues,  we  propose  a  blockchain-based  traffic  carbon  data
sharing  and  modeling  (BCSM)  method  that  provides  a  secure,
efficient, and reliable platform for carbon emissions trading. Our
approach  introduces  a  blockchain-based  framework  designed
to  ensure  data  integrity  and  user  privacy  in  carbon  markets,
thereby  enhancing  transparency  and  trust  among  participants.
We  further  develop  a  hierarchical  aggregated  carbon  trading
data  modeling  architecture  that  integrates  hypernetworks  with
attention mechanisms, enabling the creation of high-quality, per-
sonalized models for federated learning clients. This architecture
allows clients to benefit from collective insights while preserving
data  confidentiality.  Additionally,  we  implement  a  blockchain-
editable   access   control   mechanism,   facilitating   fine-grained
permissions   management   and   maintaining   a   comprehensive,
auditable  trail  of  system  interactions.  The  experimental  results
demonstrate  that  our  BCSM  approach  not  only  enhances  data
security but also significantly improves model performance, offer-
ing  a  robust  solution  to  the  challenges  in  traffic  carbon  trading
and  contributing to  the broader  energy  transition objectives.
Index Terms—Blockchain technology, federated learning, IIoT,
secure  data  sharing.
Received  17 December  2024; revised  8  March  2025  and  22 March  2025;
accepted  17  May  2025.  Date  of  publication  20  May  2025;  date  of  current
version  25  July  2025.  This  work  was  supported  in  part  by  the  Fundamental
Research  Funds  for  the  Central  Universities,  JLU  Program  under  Grant
xzy012025048 and Grant 93K172024K12, and in part by the Xi’an Jiaotong
University  Suzhou  Academy—Suzhou  Broadcasting  System  (SBS)  through
Digital  Intelligent  Media  Joint  Innovation  Consortium  Program  under  Grant
CJRH2024202.(Corresponding authors: Hongjie Liu; Fan Yang.)
Xinhuan  Zhang  is  with  the  College  of  Engineering,  Zhejiang  Normal
University, Jinhua 321004, China (e-mail: zxh@zjnu.cn).
Hongjie Liu is with the School of Computer Science and Technology, Xi’an
Jiaotong University, Xi’an 710049, China (e-mail: hj_popel@stu.xjtu.edu.cn).
Fan Yang is with the School of Computer Science and Technology, Xi’an
Jiaotong  University,  Xi’an  710049,  China,  also  with  the  Key  Laboratory  of
Symbolic Computation and Knowledge Engineering of Ministry of Education,
Jilin  University,  Changchun  130012,  Jilin,  China,  and  also  with  the  Hubei
Key  Laboratory  of  Transportation  Internet  of  Things,  Wuhan  University  of
Technology, Wuhan 430062, China (e-mail: f.yangcs@xjtu.edu.cn).
Digital Object Identifier 10.1109/JIOT.2025.3571952
## I.  INTRODUCTION
## I
N THE IIoT ecosystem, the efficient and secure modeling
and sharing of traffic carbon emissions data play a pivotal
role  in  advancing  sustainable  practices,  enabling  informed
decision-making,  and  supporting  the  global  energy  transi-
tion.  By  harnessing  advanced  algorithms  and  data  analytics
within the IIoT framework, stakeholders can derive actionable
insights into emissions patterns, optimize traffic management
systems,   and   implement   targeted   strategies   for   emissions
reduction[1],[2]. These efforts are particularly critical in the
context of global warming, which has intensified environmen-
tal  challenges,  threatening  ecological  systems  and  economic
stability   worldwide[3],[4].   To   address   these   challenges,
carbon  emission  management  has  emerged  as  a  cornerstone
of  climate  action,  with  carbon  trading  markets  serving  as  a
key  mechanism  to  incentivize  emissions  reductions.  These
markets  facilitate  the  trading  of  carbon  credits,  encouraging
industries  to  adopt  greener  practices  and  align  with  inter-
national  climate  goals.  Against  this  global  backdrop,  China
has taken significant strides in carbon emission management.
For  example,  following  its  2009  commitment  to  reduce  car-
bon dioxide emissions, China established a carbon emissions
trading  market  across  eight  pilot  provinces  and  cities.  This
initiative  has  demonstrated  remarkable  growth  in  transaction
volume  and  turnover,  highlighting  the  importance  of  robust
and  secure  data  sharing  mechanisms  to  ensure  the  market’s
scalability and effectiveness.
Current  research  on  carbon  data  sharing  highlights  the
importance of developing robust, transparent, and interopera-
ble systems to effectively track and manage carbon emissions.
Blockchain  technology  has  gained  significant  attention  for
its  potential  to  enhance  data  integrity  and  trust  in  carbon
accounting, as demonstrated in[5], where authors explored its
role  in  greening  supply  chains.  However,  critical  challenges
remain,  particularly  in  the  context  of  carbon  trading  data
model sharing and data privacy assurance mechanisms. Issues
such as the lack of standardized data formats, the complexity
of  handling  nonindependent  and  identically  distributed  (non-
IID)   data   in   decentralized   systems,   and   the   difficulty   of
ensuring privacy while maintaining data utility are significant
barriers[6]. Furthermore, the integration of federated learning
with blockchain, though promising, faces scalability and com-
putational efficiency challenges, as demonstrated in[7]. While
existing studies have made progress in addressing these chal-
lenges, they often fall short in providing a holistic solution that
## 2327-4662
c
2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies.  Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ENHANCED TRAFFIC CARBON EMISSIONS DATA SHARING AND MODELING31065
combines secure data sharing, efficient modeling, and privacy
preservation.  This  study  improves  upon  previous  efforts  by
introducing   a   novel   framework   that   integrates   blockchain
and  personalized  federated  learning,  offering  enhanced  data
security,  improved  handling  of  non-IID  data,  and  scalable
privacy-preserving  mechanisms.  Addressing  these  issues  is
essential  for  advancing  carbon  data  sharing  and  achieving
global climate goals.
Existing research highlights key challenges in carbon trad-
ing  data  sharing  and  modeling  that  hinder  effectiveness  and
reliability[8].   A   major   issue   is   inadequate   data   storage
security, as centralized repositories are vulnerable to breaches
and  unauthorized  access[9],  risking  data  integrity  and  trust.
Collaborative  training  mechanisms  for  local  models  are  also
inefficient, as organizations prioritize data privacy, leading to
slow and costly model aggregation[10]. Additionally, current
data  access  control  mechanisms  lack  granularity,  resulting  in
insufficient  oversight  and  potential  misuse[11].  Addressing
these challenges requires enhanced security, optimized training
processes,  and  improved  access  controls  to  support  effective
carbon trading and sustainable energy transitions. Therefore, in
response to the challenges associated with carbon trading data
model sharing and data privacy assurance, we propose a carbon
trading data sharing and training model that employs federated
learning along with robust privacy assurance mechanisms. This
approach addresses the privacy risks and model inefficiencies
inherent in traditional carbon trading data sharing models. The
main contributions of our work are as follows.
1)  This  article  proposes  a  blockchain-based  traffic  carbon
emissions  data  sharing  and  modeling  (BCSM)  frame-
work,  prioritizing  data  integrity  and  user  privacy.  By
leveraging blockchain and federated learning, the BCSM
framework  decentralizes  data  processing  while  ensur-
ing  data  remains  local  to  clients,  addressing  privacy
concerns  in  hierarchical  systems[11],[12].  This  com-
bination  enhances  scalability,  data  security,  and  trust
among  participants,  overcoming  limitations  in  peer-to-
peer frameworks[13].
2)  We introduce a hypernetwork and attention mechanism-
based  hierarchical  aggregation  architecture  for  carbon
trading  data  modeling,  enabling  high-quality,  personal-
ized federated learning models. This approach optimizes
the  loss  function  across  clients,  addressing  the  lack  of
personalization  in  prior  studies[11],[12].  By  continu-
ously updating models with real-time data, it overcomes
the  rigidity  and  optimization  challenges  of  traditional
smart contracts[14].
3)  We  propose  a  blockchain-based  access  control  method
for  carbon  trading  data  and  models,  providing  fine-
grained  controls  and  maintaining  an  auditable  trail  of
changes. This reduces risks of data manipulation, unau-
thorized  access,  and  fraud,  fostering  trust  and  integrity
in  the  carbon  trading  ecosystem.  Compared  to  earlier
research[14],  it  offers  greater  flexibility  to  adapt  to
diverse regulatory and market conditions.
The   remainder   of   this   article   is   structured   as   follows.
SectionIIreviews related research on blockchain and carbon
trading.  SectionIIIintroduces  the  key  BCSM  approaches
and  algorithms.  In  SectionIV,  we  present  a  comprehensive
security analysis of the BCSM system. SectionVdetails exten-
sive  experiments  comparing  and  analyzing  the  security  and
effectiveness of our proposed model. Finally, SectionVIsum-
marizes  the  main  contributions  of  this  research  and  suggests
future research directions.
## II.  R
## ELATEDWORK
This  section  reviews  related  research  by  examining  two
critical  aspects.  First,  we  explore  advancements  and  appli-
cations  in  blockchain  and  federated  learning  technologies,
highlighting  their  potential  to  enhance  security  and  trust  in
data  management.  Second,  we  focus  on  carbon  data  sharing,
discussing its role in promoting transparency and collaboration
in efforts to mitigate climate change.
A.  Blockchain and Federated Learning
Blockchaintechnology,firstintroducedbySatoshi
Nakamoto,  represents  a  groundbreaking  innovation  that  has
profoundly  impacted  various  sectors of the modern  economy
and  society[15].  As  a  decentralized  and  transparent  ledger
system,  blockchain  enhances  security  and  trustworthiness  in
transactions by eliminating the need for intermediaries. In the
realm of blockchain research, Zhaofeng et al.[16]introduced
BlockTDM,   a   blockchain-based   data   management   scheme
tailored  for  edge  computing.  This  scheme  offers  a  flexible
and configurable framework, featuring a mutual authentication
protocol,  flexible  consensus,  smart  contract  implementation,
as well as block and transaction data management, and node
management.  Blockchain  technology  is  frequently  employed
to develop systems aimed at protecting private data, in addition
to  its  applications  in  secure  carbon  trading  data  storage  and
training systems.
To    address    the    challenges    posed    by    data    islands,
Qu et al.[17]developed the D2C paradigm, which integrates
blockchain  and  federated  learning.  This  approach  provides
privacy   protection,   efficient   processing,   and   decentralized
incentives  while  being  resilient  against  poisoning  attacks.
Furthermore, Xu et al.[18]proposed a method that leverages
blockchain  to  validate  Laplace  noise  in  query  results,  along
with  an  anonymous  data  publication  mechanism  that  ensures
data utility without compromising the integrity of the publisher
or recipient.
Federated  learning  aims  to  enable  efficient  machine  learn-
ing  across  multiple  participants  or  computing  nodes  while
safeguarding   data   privacy   and   security.   Unlike   traditional
approaches  that  involve  sharing  raw  data,  federated  learn-
ing  operates  by  exchanging  model  parameters  or  updates,
thereby minimizing the risk of exposing sensitive information.
This  framework  ensures  the  protection  of  endpoint  and  per-
sonal   data   while   maintaining   compliance   with   legal   and
regulatory  requirements[10],[19],[20],[21],[22].Inthis
context, Ye et al.[23]introduced a novel aggregation method
called federated learning with discrepancy-aware collaboration
(FedDisco). This method considers both the size of the dataset
and  the  discrepancies  between  local  models  during  aggrega-
tion. By incorporating these factors into the weighting process,
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

## 31066IEEE INTERNET OF THINGS JOURNAL, VOL. 12, NO. 15, 1 AUGUST 2025
FedDisco  provides  a  tighter  theoretical  bound  for  optimizing
errors.  This  approach  enhances  the  utility  and  modularity  of
the federated learning process while maintaining efficiency in
both communication and computation.
## B.  Carbon Emissions Data Sharing Research
Recent  studies  have  focused  on  carbon  emissions  data
sharing  and  modeling,  exploring  various  methodologies  and
frameworks  aimed  at  enhancing  the  efficiency  and  effective-
ness of carbon trading systems. However,  challenges such as
low  data  sharing  efficiency  and  insufficient  model  person-
alization  continue  to  persist.  In  the  field  of  carbon  trading,
Chang  et  al.[24]developed  an  interactive  system  dynamics
model  to  illustrate  the  internal  relationships  among  carbon
emission trading, tradable green certificates, and the electricity
market. This model explores the interconnectedness of various
markets through the investment behaviors of participants and
the mechanisms of price formation. The analysis highlights the
dynamic equilibrium processes across these markets, reflecting
the current state of electricity market reforms in China.
Recent   studies   have   demonstrated   the   effectiveness   of
carbon  emission  trading  systems  (ETS)  in  reducing  emis-
sions  and  driving  economic  outcomes.  Zhang  et  al.[25]
applied  a  difference-in-difference  approach  to  city-level  data
in   China,   revealing   a   16.2%   reduction   in   carbon   emis-
sions  in  pilot  regions,  with  stronger  effects  in  economically
developed  eastern  China.  Similarly,  Yang  et  al.[26]uti-
lized a difference-in-differences  framework, showing that the
pilot  ETS  significantly  influenced  both  employment  growth
and  emission  reductions.  In  predictive  modeling,  Huang  and
He[27]introduced   an   unstructured   learning   method   for
carbon price forecasting, achieving high accuracy, while[28]
proposed  a  hybrid  approach  combining  decomposition  tech-
niques  and  long  short-term  memory  networks,  which  also
exhibited superior predictive performance.
Significant   advancements   have   been   made   in   enhanc-
ing  data  sharing  and  security  within  carbon  ETS.  Pan  et
al.[29]developed  a  system  dynamics  model  to  evaluate
the  ETS  and  analyze  its  internal  components,  while[30]
proposed   a   two-phase   data   envelopment   analysis   method
to   assess   resource   allocation   under   strict   carbon   quotas.
Blockchain   technology   has   been   increasingly   adopted   to
improve  system  efficiency  and  transparency.  For  instance,
Hu et al.[9]designed  a  blockchain-enabled  distributed  ETS
(BD-ETS)  using  Hyperledger  Fabric,  transitioning  from  cen-
tralized   to   decentralized   trading.   Al   Sadawi   et   al.[12]
leveraged   blockchain’s   security   and   traceability   to   effec-
tively  track  carbon  emission  reductions.  Further  innovations
include[31],  who  simulated  carbon  allocation  under  varying
unpaid  quota  conditions,  and[32],  who  established  a  trans-
parent  and  incentivized  ETS  using  Hyperledger  and  smart
contracts.
Despite   progress,   challenges   remain   in   carbon   trading
data  sharing  efficiency  and  model  personalization,  as  current
systems  often  lack  the  flexibility  and  security  required  for
transparent  and  efficient  operations.  A  secure  and  effective
framework is urgently needed to enhance data sharing, ensure
transparency,  and  establish  robust  incentive  mechanisms  for
Fig. 1.Basic framework for two different training schemes. (a) Centralized
training. (b) Federated training.
stable market operations. Addressing these gaps is vital for the
evolution of carbon ETSs. In this study, we propose integrating
blockchain  and  federated  learning  to  create  an  incentivized
carbon trading system that improves efficiency and scalability.
Beyond  addressing  security,  data  sharing,  and  traceability,
our research highlights the importance of robust carbon price
prediction  models,  an  often-overlooked  aspect.  By  enabling
secure data sharing and developing reliable predictive models,
our   work   aims   to   advance   the   carbon   neutrality   market
significantly.
## III.  B
## LOCKCHAIN-BASEDCARBONTRADINGDATA
## SHARING ANDMODELING
A.  Blockchain and Federated Learning
Blockchain  technology  is  a  decentralized  and  distributed
approach  to  data  management  that  employs  cryptographic
techniques  to  ensure  both  security  and  tamper  resistance.
Each  block  in  the  blockchain  contains  information  from  all
previous  blocks  and  is  maintained  by  multiple  nodes,  which
collectively  ensure  the  security  and  transparency  of  the  data.
Due to its inherent decentralization and high-security features,
blockchain  technology  has  found  applications  across  various
domains,  including  digital  currencies,  smart  contracts,  data
storage, and more[18],[33],[34],[35].
A critical aspect of blockchain technology is its consensus
mechanism, which allows multiple nodes to reach agreement
and confirm transactions through specific algorithms, eliminat-
ing  the  need  for  centralized  supervision.  Additionally,  smart
contracts,   which   are   self-executing   agreements   embedded
within the blockchain, automatically enforce contractual terms
without  requiring  human  intervention,  thereby  reducing  the
risk  of  fraud.  The  advancements  in  blockchain  technology
offer promising solutions for the efficient storage and sharing
of  carbon  trading  data  and  for  facilitating  federated  model
training within this domain.
Federated   learning   is   a   distributed   machine   learning
paradigm  that  builds  models  without  transferring  data  from
local  devices.  Unlike  centralized  training,  which  risks  client
privacy by uploading data to a central server, federated learn-
ing  enables  collaborative  model  development  without  direct
data  sharing.  As  shown  in  Fig.1,  federated  learning  uses
encryption  to  protect  parameter  information,  ensuring  data
confidentiality. This technology supports collaborative carbon
trading data-sharing models, enhancing privacy protection and
fostering innovation in carbon trading practices.
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ENHANCED TRAFFIC CARBON EMISSIONS DATA SHARING AND MODELING31067
The  blockchain  used  in  this  study  is  a  private  blockchain,
offering  advantages  such  as  enhanced  controllability,  lower
transaction costs, and improved privacy protection for carbon
trading  data  sharing  and  modeling.  Managed  by  trusted  enti-
ties, private blockchain nodes reduce energy consumption and
latency  compared  to  public  blockchains  while  ensuring  data
security and traceability. In this framework, the server aggre-
gates  and  coordinates  model  parameters  (e.g.,  gradients  or
weights) in federated learning without accessing raw user data,
eliminating leakage risks. Decentralization is achieved through
blockchain’s distributed storage and transparent access control,
with  the  server  solely  coordinating  training,  aligning  with
decentralized  principles.  This  hybrid  architecture  combines
blockchain’s  decentralization  with  federated  learning’s  effi-
ciency, ensuring data privacy and cost-effective model training.
Private  blockchain’s  limited  nodes  and  trusted  management
further lower operational costs and energy consumption, while
the  server’s  minimal  computational  demands  enhance  overall
efficiency. In summary, this design balances data privacy and
efficient training, leveraging private blockchain and federated
learning for scalability and economic viability.
B.  Architecture and Security Model in BCSM
We  now  describe  the  BCSM  scheme,  which  is  designed
to  facilitate  efficient  data  sharing  and  the  training  of  carbon
trading  data  models  within  a  distributed  environment.  The
interactions among the modules in this system are divided into
four stages: 1) contract deployment; 2) requirements matching;
3) preparation for execution; and 4) contract execution.
1)  HierarchicalShapleyDelegatedProof-of-Stake
Consensus  Mechanism  :The  success  of  a  carbon  trading
data modeling and training system relies on active participant
engagement   in   data   sharing.   Federated   learning   enables
contributors  to  enhance  model  performance  while  preserving
data   privacy   and   security,   fostering   collaborative   efforts
toward accurate carbon trading strategies. However, equitably
assessing individual contributions and ensuring mutual benefits
for participants and the community remain critical challenges.
To address this, we propose the hierarchical Shapley delegated
proof   of   stake   (HSDPS)   mechanism.   HSDPS   combines
Shapley  values,  which  ensure  fair  reward  distribution  based
on  contributions,  with  the  Delegated  Proof  of  Stake  (DPoS)
model,    enabling    decentralized    decision-making    through
voting.  This  hierarchical  consensus  structure  prevents  power
monopolization by any single master node, enhancing fairness,
transparency,  and  network  security[36].  If  a  majority  of
nodes  deem  the  master  node  malicious  or  ineffective,  they
can  remove  it  and  elect  a  new  one,  ensuring  accountability
and system integrity.
At the start of each term, nodes interested in becoming the
master node submit candidacies with local logs demonstrating
their contributions and data integrity. Candidates compete for
peer trust by showcasing ethical practices and commitment to
the system’s success. The node with the most credible log, as
voted  by  the  majority,  assumes  the  master  role.  This  demo-
cratic  process  encourages  positive  behavior  and  meaningful
contributions, fostering a resilient ecosystem for secure carbon
Algorithm  1Hierarchical  Proxy  Proof-of-Stake  Consensus
Mechanism HSDPS
Require:Shared  carbon  trading  data  for  nodes  involved  in
federated learning.
1:whileIn a consensus loopdo
2:Every participant votes based on their contribution.
3:Sort the vote results to get sorted_vote_list.
4:Select    theNhighest    voted    delegates    from    the
sorted_vote_list.
5:delegates←getMdelegates from sorted_vote_list.
6:Random disorder delegates←shuffle(delegates).
7:forPick out the packing nodedo
8:To  get  the  slot,  multiply  the  hash  of  the  previous
block by the interval of the last created block.
## 9:slot←pre_block_hash/block_interval.
10:To  obtain  the  representative  index,  use  slot  to  take
moduloM.
11:index←slot  modM
12:ifThe current node is delegates[index]then
13:ifCurrent node status is coordinatorthen
14:Add the coordinator’s contribution of federated
learning to the account.
15:end if
16:Record  each  participant’s  contribution,  verify  it
using each party’s public key, then sign the trans-
action with the public key.
17:Add   participantito   the   pool   with   other   par-
ticipants  in  different  orders  and  calculate  their
average  marginal  returns  and  calculatem(i)=
## 1
n!
## ∑
## S
## [
v
## (
## N
## S
i
## ∪i
## )
## −v
## (
## N
## S
i
## )]
## .
## 18:generate_block(sign
sk
## (verified_transaction))
## 19:else
## 20:skip
21:end if
22:end for
23:end while
trading   data   collection,   modeling,   and   sharing,   ultimately
advancing  sustainable  climate  action.  Algorithm1outlines
the  proxy  proof-of-stake  consensus  mechanism,  HSDPS,  as
implemented in our system.
In  Algorithm1,  the  consensus  mechanism  focuses  on  rep-
resentatives  who  perform  critical  roles  such  as  bookkeeping,
monitoring,  and  coordination.  The  election  process  identifies
the  topNaccounts  with  the  most  votes,  who  then  become
system representatives responsible for block packaging, coor-
dinating federated learning, and receiving incentives.
The  Shapley  game  employs  a  profit-sharing  method  that
evaluates  individual  contributions  with  greater  precision  than
union   game   techniques.   By   accounting   for   variations   in
rewards  based  on  the  sequence  of  member  participation,  it
ensures  a  fair  and  accurate  assessment  of  each  participant’s
input,  fostering  fairness  and  encouraging  active  engagement,
which enhances system success. After federated learning, the
coordinator  or  bookkeeping  node  receives  a  fixed  reward,
while  data  providers  are  compensated  based  on  their  contri-
butions. The Shapley revenue-sharing-based HSDPS protocol
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

## 31068IEEE INTERNET OF THINGS JOURNAL, VOL. 12, NO. 15, 1 AUGUST 2025
involves  a  single  election  per  consensus  cycle,  with  new
candidate   representatives   elected   at   the   cycle’s   end.   This
process  ensures  the  continuous  involvement  of  active  and
productive  members,  promoting  fairness  and  sustainability
within the system.
C.  Primary Steps of Federated Training in the BCSM Scheme
The  BCSM  scheme  achieves  both  efficiency  and  security
in  the  collaborative  modeling  of  carbon  trading  data  through
effective  storage  and  sharing,  combined  with  a  personalized
federated  learning  approach.  The  system  is  built  on  three
critical  security  aspects,  which  are  discussed  in  detail.  One
primary concern  is protecting against  data theft from partici-
pating nodes. As previously mentioned, BCSM manages three
main types of data: 1) intermediate data generated during smart
contract  execution;  2) source data; and 3) the final  results of
data analysis. The key steps involved in the system’s operation
are outlined as follows.
1)Initialization:This  phase  involves  initializing  the  fol-
lowing system parameters.
a)  Managers   utilize   the   Installation   procedure   to
select the public carbon trading data model param-
eters  for  the  blockchain.  These  parameters  are
included in the first block (i.e., the genesis block).
b)Contract Deployment:The manager uses the Enroll
method  to  generate  a  long-term  account  based  on
the  characteristics  specified  in  the  genesis  block.
Once this account is established, the manager sub-
mits the constructed smart contract as a transaction
to the  blockchain.  The  smart  contract  is deployed
on  the  blockchain  after  successfully  passing  the
validation procedure.
c)Generating and Sharing Keys:
i)  TA   (Trusted   Authority)   generates   the   pub-
lic/secret  keys  for  each  usern(n∈L,|L|=
N).  Here,(δ, ρ)andK=(K
## 1
## ,K
## 2
)are  the
secret  keys  used  in  homomorphic  hash  func-
tions and pseudorandom functions, respectively.
## (N
## PK
n
## ,N
## SK
n
)and(P
## PK
n
## ,P
## SK
n
)are  employed  to
encrypt usern’s local gradientx
n
## .
ii)  Usernsends the public keys(N
## PK
n
## ,P
## PK
n
)to the
cloud server through a secure channel.
iii)  Server  Side  receives  messages  from  at  leastt
users (represented as.L
## 1
⊆L), wheretis the
threshold  of  the  Shamir’st-out-of-Nprotocol
used   in   our   system.   If   fewer   thantusers
participate, the process is aborted and restarted.
The  server  then  broadcasts{m,N
## PK
m
## ,P
## PK
m
## ,τ=
sum}
m∈L
## 1
to  each  user∈L
## 1
,  whereτ=sum
represents the statistical label to be calculated.
2)Registration   for   Aggregated   Carbon   Trading   Data
Model:This  phase  involves  registering  two  types  of
entities:  1)  users  and  2)  managers.  To  register  a  user,
the  system  retrieves  the  settings  from  the  blockchain
(e.g.,  for  Alice)  and  establishes  a  long-term  account
## (pk
m
## =Q
m
## ,sk
m
## =d
m
)via the Enroll method. Manager
registration follows the same process as user registration.
However, in our approach, managers share ownership of
the same long-term account, which is used only for trac-
ing purposes, not for transaction issuance or consensus.
Consequently,  the  registration  operation  is  performed
only  once,  and  the  obtained  long-term  accountpk
m
is
used a single time.
3)Chain  Transaction:Managers  append  pending  transac-
tions  to  the  blockchain  by  first  confirming  the  validity
of  the  obtained  data,  denoted  as(tx,s).  For  example,
to  assess  Alice’s  transaction(tx
a
## ,s
a
),  managers  begin
by   parsing   the   transaction,   structured   asa,pk
a
## =
## (Q
## 
a
## ,Q
## 
a
), along with the accompanying proofπ
a
.Using
their private keysk
m
, the managers trace the long-term
address associated with the public keypk
a
## =(Q
## 
a
## ,Q
## 
a
## ).
This  process  involves  invoking  the  Trace  function  to
retrieve  Alice’s  underlying  public  key,pka.  Following
this retrieval, theisLegalfunction is called to determine
whetherpkahas been flagged as banned or involved in
illicit activities. IfisLegalindicates thatpkais banned,
the  corresponding  pending  transactiontx
a
is  rejected.
This systematic approach not only ensures the integrity
of  the  blockchain  by  preventing  unauthorized  transac-
tions but also reinforces trust within the carbon trading
ecosystem  by  allowing  only  legitimate  participants  to
engage  in  transactions.  The  chain  transaction  phase  is
therefore crucial in maintaining the overall security and
reliability of the system.
4)Federated Training Gradient Updates:
a)  Verify  whetherL
## 3
## ⊆L
## 2
and|L
## 3
|≥t.  If  not,
abort  and  start  over.  Decrypt  eachP
n,m
form∈
## L
## 2
\{n}asn	m	N
## SK
n,m
β
n,m
←AE.dec(.KA.agree
## .(P
## SK
n
## ,P
## PK
m
## ),P
n,m
).  Send{(N
## SK
n,m
)|m∈L
## 2
## \L
## 3
## }
and{(β
n,m
)|m∈L
## 3
}to the cloud, whereL
## 2
## \L
## 3
represents  users  who  have  sent  data  to  the  server
but dropped out before uploading data to the cloud
server.
b)  Receive messages from at leasttusers (represented
as.L
## 4
## ⊆L
## 3
); otherwise, abort and start over.
c)  CalculateN
## SK
n
←S.recon({N
## SK
n,m
## }
m∈L
## 4
## ,t).
d)  Calculateβ
n
←S.recon({β
n,m
## }
m∈L
## 4
## ,t).
D.  Method for Carbon Trading Data Modeling
1)  Local  Carbon  Trading  Data  Modeling  Method:The
carbon  trading  data  modeling  process  can  be  both  time-
consuming  and  costly,  largely  due  to  the  need  for  manual
model   design   and   tuning.   To   address   this   challenge,   we
propose  an  economical  neural  architecture  search  (E-NAS)
solution  that  automates  this  process.  E-NAS  employs  neu-
ral   architecture   search   techniques   to   automatically   design
high-performance  network  structures  based  on  sample  sets.
This   approach   rivals,   and   in   some   cases   surpasses,   the
expertise  of  human  professionals,  often  discovering  novel
network structures previously unexplored by human designers.
Consequently,  implementing  neural  networks  becomes  more
efficient and less resource-intensive[37].
E-NAS offers an automated and efficient solution for carbon
trading  data  modeling  by  minimizing  human  involvement
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ENHANCED TRAFFIC CARBON EMISSIONS DATA SHARING AND MODELING31069
in  model  design  and  tuning.  It  identifies  optimal  training
hyperparameters  within a predefined  cell-based search space,
where  networks  are  composed  of  normal  and  reduction  cells
connected  in  a  specific  pattern,  with  each  cell  initialized  by
the  outputs  of  the  preceding  two  cells.  To  further  enhance
efficiency,   we   employ   a   carbon   trading   data   importance
pruning  strategy  that  retains  only  the  most  critical  hyperpa-
rameters. This involves sampling configurations with minimal
computation time, using random forest techniques to estimate
hyperparameter importance, and iteratively pruning less impor-
tant hyperparameters by setting them to values with the lowest
computational  cost.  This  streamlined  approach  ensures  accu-
rate  and  efficient  model  creation  while  maintaining  optimal
performance  in  carbon  trading  data  modeling.  We  introduce
a  category  distribution  related  to  the  computational  cost  for
every element in
i
c
## (
ζ
i,j
## )
## =
exp
## {
## −Z
## (
## 
i,j
## )}
## ∑
j
exp
## {
## −Z
## (
## 
i,j
## )}
## (1)
where  the  number  of  floating-point  operations  is  represented
by  the  functionZ(
i,j
).  We  generate  a  setDwith  different
subsetsx
ref
## ,x
pos
, andx
neg
after repeating the prior operations
K=20 times. This set is used as a training set for the random
forest,  where  the  trees  are  constructed  using  replacement
sampling fromD.
The reduction in node impurity, weighted by the number of
samples reaching the node, is used to compute the significance
of  each  parameter  at  nodemin  the  regression  tree.  The
significance parameter for nodemis defined as follows:
## O
m
## =
## |
## P
m
## |
## H
## (
## P
m
## )
## −
## ∣
## ∣
## P
pos,m
## ∣
## ∣
## H
## (
## P
pos,m
## )
## −
## ∣
## ∣
## P
neg,m
## ∣
## ∣
## H
## (
## P
neg,m
## )
## (2)
where
## H
## (
## P
m
## )
## =
## ∑
c
ref,i
## ∈P
m
## (
c
ref,i
## −c
ref,P
m
## )
## 2
## |P
m
## |
## .(3)
After  estimating  the  importance  of  hyperparameters,  the
hyperparameter  with  the  lowestO
m
is  pruned  by  setting  it
to  the  value  associated  with  minimal  resource  consumption.
This pruning process significantly enhances search efficiency.
By  reallocating  computational  resources  from  less  important
hyperparameters to more critical ones, we optimize the over-
all  efficiency  and  performance  of  the  carbon  trading  data
modeling process.
## 2)  Explainable  Carbon  Trading  Data  Modeling  Method:
Carbon trading data evaluation evidence with zero knowledge
proof  is  used  by  institutions  or  regulators  to  validate  the
legitimacy of the user’s carbon trading data source. The model
and  data  utilized  are  those  obtained  in  the  preceding  part
using  the  federated  Average  technique.  Algorithm3presents
our  proposed  local  interpretable  carbon  trading  data  model-
agnostic  explanations  algorithm.  In  terms  of  carbon  trading
data  model  interpretability,  we  utilize  a  Tree-interpreter  that
follows the decision path and attributes changes in prediction
to each feature along the prediction path. The Tree-interpreter
leverages Equation as follows:
f(x)=
## G
## ∑
k=1
## (
## 1
## U
## U
## ∑
u=1
contribution
u
## (x,g)
## )
## +
## 1
## U
## U
## ∑
u=1
## L
j
## (4)
whereUrepresents the number of trees,L
j
is the average bias
from the complete dataset, andGis the total number of carbon
trading data features.
In our federated feature selection design, only one federated
server is required to compute and compare mutual information
values  and  choose  features.  The  server  will  be  able  to  tell
clients whose featureIDs have been picked in this manner, but
it will not know the particular feature(s) or the original data.
Clients can prepare the selected part of their feature data for
the  subsequent  job  in  the  vertical  federated  learning  because
they know which part of their feature data is picked based on
the feature-IDs given by the server.
E.  Personalized Federated Training Scheme Based on
Personalized Weight Generation Mechanism for
## Hypernetworks
To  enable  personalized  and  efficient  carbon  trading  data
sharing  and  training  in  a  distributed  environment,  we  pro-
pose  a  method  integrating  hypernetwork  aggregation  with  an
attention  mechanism  for  federated  model  construction.  This
approach  enhances  individual  contributions  while  optimizing
overall   model   performance.   Fig.2illustrates   the   person-
alized  federated-learning-based  carbon  trading  data  sharing
framework. Hypernetwork aggregation generates unique repre-
sentations for each contributor, while the attention mechanism
prioritizes  relevant  data  points,  improving  training  efficacy.
This  dual  strategy  enhances  data  sharing  and  fosters  collab-
oration, enabling participants to maximize their contributions
and build robust carbon trading models.
In  traditional  federated  learning,  the  iterative  update  of
the  global  model  benefits  from  data  collected  from  different
regions,  devices,  and  organizations,  thereby  improving  the
model’s   performance   and   generalization.   Under   the   inde-
pendent  and  identically  distributed  (IID)  setting,  the  update
direction  of  client  local  models  shows  minimal  variation,
leading  to  a  global  model  optimization  direction  that  closely
aligns with that of the local models, as illustrated in Fig.3(a).
However, under the Non-IID setting, significant differences in
the  update  direction  of  weights  among  clients  can  occur,  as
showninFig.3(b). In such cases, broadcasting the aggregated
global model to the clients can cause the local models to start
iterative training from a low starting point again, slowing down
the  convergence  speed  of  the  global  model  and  resulting  in
suboptimal performance on client local carbon trading data.
To  fully  harness  the  potential  within  the  data,  our  model
incorporates  an  attention  mechanism  designed  to  enhance
feature  representation.  The  first  phase,  known  as  Feature
Extraction,  captures  global  features  from  the  feature  maps
generated  by  a  convolutional  block.  For  a  designated  feature
mapY∈R
## C×W×H
,  we  employ  an  extractoreto  derive
features,  represented  mathematically  asE=e(Y,w
e
),  where
w
e
denotes  the  parameters  governing  the  extraction  process
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

## 31070IEEE INTERNET OF THINGS JOURNAL, VOL. 12, NO. 15, 1 AUGUST 2025
Fig.  2.Framework  for  hierarchical  aggregate  learning  based  on  federated  learning  begins  with  the  initialization  of  the  hypernetwork,  client  localcarbon
trading  data  models,  and  embedded  carbon  trading  data  models.  Key  parameters,  such  as  the  total  number  of  communication  rounds,  target  accuracy  for
federated learning, number of iterative local updates per client during each communication round, and the number of clients participating in each round are
established. Subsequently, clients conduct local training according to these predefined parameters. Once local training is completed, clients share their updated
parameters, which are then aggregated to update the global model, leveraging collaborative insights while maintaining carbon trading data privacyand security.
Fig.  3.Example  of  parameter  update  direction  deviation  in  carbon  trading
data sharing process due to client drift under (a) IID and (b) Non-IID settings
in the distributed environment.
andEsignifies the resulting feature set. The flexibility inherent
ineallows it to produce a variety of feature patterns depending
on the specific extraction techniques applied, thereby enabling
the  model  to  adapt  effectively  to  the  diverse  characteristics
of  the  data.  The  subsequent  phase,  Transformation,  reshapes
these   extracted   features   into   a   nonlinear   attention   space,
depicted  ast,  where  the  output  of  the  attention  block  is
expressed asK=t(E,w
t
## ). Here,w
t
represents the parameters
used during the transformation process, whileKindicates the
output from the proposed attention mechanism. By transform-
ing  the  extracted  features  into  this  more  complex,  nonlinear
space,  the  model’s  ability  to  identify  intricate  relationships
and  dependencies  among  data  points  is  enriched.  This  dual-
stage   approach   not   only   optimizes   the   feature   extraction
process  but  also  enhances  the  overall  learning  efficacy  of
the   framework,   making   it   particularly   adept   at   uncover-
ing   critical   insights   in   complex   domains   such   as   carbon
trading.
Fig. 4.Schematic of the workflow of the hypernetwork.
We  propose  a  hypernetwork-based  mechanism  for  gener-
ating  personalized  weights  in  federated  learning.  As  shown
in  Fig.4,  the  hypernetwork  produces  a  weight  matrix  for
the   attention   layer   within   a   self-attention   framework.   Its
hidden  layers  learn  relationships  between  label  embeddings,
while the output layer generates a personalized weight matrix
tailored   to   each   client’s   attention   layer   architecture.   The
hypernetwork  operates  independently  of  the  client’s  model
structure,  enabling  flexible  model  and  attention  mechanism
selection while preserving data privacy. This design allows the
hypernetwork to adapt to diverse tasks and label embeddings,
enhancing compatibility and scalability. By fostering efficient,
privacy-preserving learning, it supports intelligent carbon trad-
ing mechanisms and advances sustainable development goals.
Given  that  carbon  trading  data  is  stored  on  a  blockchain,
as  described  in  previous  sections,  we  propose  a  federated
training   mechanism   tailored   for   our   carbon   trading   data
model,  considering  the  decentralized  and  distributed  nature
of   blockchain   storage.   The   carbon   trading   data   of   each
node  is  obtained  in  a  distributed  manner  across  multiple
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ENHANCED TRAFFIC CARBON EMISSIONS DATA SHARING AND MODELING31071
Algorithm  2Hierarchical  Aggregation  Algorithm  Based  on
Hypernetworks and Attention Mechanisms
Require:Global carbon trading data model parameters
1:Initialize the data sharing model parameters	and broad-
cast them to all participating nodesp
i
for model training
2:foreach  global  carbon  trading  data  model  update  round
k=1,2,3, ...do
3:foreach participating nodep=1,2,3, ...do
4:Access carbon trading data from the blockchain
5:Get the  features selected  by  federated  feature selec-
tion
6:Update  local  carbon  trading  data  model  parameters

## (i)
k+1
## ←
k
7:Send  the  updated  model  parametersω
## (i)
k+1
and  loss
functionL
## (i)
k+1
to the coordinator
8:end for
9:The coordinator sends the aggregated model parameters
ω
## (i)
k+1
to all participating nodes.
10:end for
11:Participating nodes perform local model updates(i, ̄w
k
## )
12:forEach iteration from 1 to local iteration numberkdo
13:Randomly divide the mental carbon trading datasetD
i
intoBbatches
14:Set  the  model  parameters  from  the  previous  iteration
as the initial parameters for the current iterationω
## (i)
## 1,t
## =
ω
## (i)
## B,t−1
## .
15:Receive the parametersw
t
i
## ,ξ
t
i
andZ
i
uploaded by all
selected  clients  or  wait  for  the  time  limit  be  reached:
Calculated using the federated learning algorithm
## ̄
ξ
t
## =
## ∑
i
m
i
## M
ξ
t
i
16:forEach  iteration  from  1  to  local  iteration  numberB
do
17:Calculate gradient valuesφ
## (b)
i
## .
18:Update  local  model  parametersω
## (i)
b+1,t
## ←ω
## (i)
b,t
## −
ηφ
## (b)
i
## .
19:end for
20:end for
21:At  the  end  of  all  communication  rounds,  send  global
model layer parameters
## ̄
ξ
## T
and the personalization param-
etersW
i
generated by the hypernetwork according to the
setZto all clients
nodes  for  feature  extraction.  The  model  is  initially  trained
locally,  and  then  the  carbon  trading  data  model  parame-
ters  are  aggregated  for  global  model  training.  Algorithm1
describes   the   detailed   process   of   the   federated   training
mechanism.
In Algorithm2, each locally acquired mental carbon trading
data will first train the local carbon trading model and provide
the  parameters   to  the  coordinator.   The  main   role  of   the
coordinator is a node that is responsible for aggregating each
local model parameter and using the parameters for the global
model.
Algorithm3DecryptAuthorizationInformationin
Blockchain-Based Carbon Transaction
InputInput OutputOutputTX;SK
## RSA
TokenList Issuer,
Subject←TX;
TXis not NULLKey
## AES
## Enc
,TokenList
## Enc
## ←TX;
## Key
## AES
←RSA.Dec(SK
## RSA
,Key
## AES
## Enc
## );
TokenList←AES.Dec(Key
## AES
,TokenList
## Enc
## );
TokenList←∅;
TokenList;
Algorithm  4Collect All Relevant Public Keys
InputInput  OutputOutputTX  AllPmtchPk:  Set  of  all  relevant
PMTCH public keysAllPmtchPk←∅;
CurrentTx←TX;
CurrentTxis   not   NULLAllPmtchPk←AllPmtchPk∪
{PMTCH public key ofCurrentTxissuer};
CurrentTx←Reference transaction ofCurrentTx;
AllPmtchPk;
F.  Access Control Algorithm in Carbon Data Sharing
In this section, we introduce the algorithms responsible for
managing  authorization  within  the  editable  blockchain-based
carbon   trading   framework.   Specifically,   Algorithms3and
4are   developed   to   decrypt   the   authorization   information
linked  to  specific  transactions.  This  process  is  essential  for
safeguarding sensitive authorization details, ensuring they are
only  accessible  to  authorized  parties  while  preserving  data
confidentiality throughout the transaction process.
Algorithms3and4are  integral  to  the  system  as  they
perform  a  recursive  query  of  all  referenced  upstream  autho-
rization  transactions.  These  algorithms  gather  all  pertinent
multitier blockchain cryptographic (TBC) public keys, forming
a comprehensive set known asAllPmtchPk. This set includes
the public  keys  of  not  only  the current  transaction  issuer  but
also  all  upstream  transaction  issuers,  thereby  establishing  a
robust network of authorization links.
The  effective  decryption  of  authorization  information  and
the comprehensive compilation of public keys are crucial for
upholding  the  integrity  and  transparency  of  carbon  trading.
These  algorithms  facilitate  access  to  transaction  authoriza-
tions  and  improve  the  overall  reliability  of  the  blockchain
framework.  By  making  all  pertinent  keys  easily  accessible,
the  system  enhances  accountability  and  traceability,  which
are  vital  for  building  trust  among  stakeholders  in  carbon
trading markets. This systematic approach aims to enhance the
efficiency  and  security  of  carbon  trading  mechanisms  in  the
context of advancing environmental sustainability.
By  implementing  methods,  such  as  decrypting  authoriza-
tion information in blockchain-based carbon transactions and
collecting all relevant public keys, we establish secure access
control  for  data  sharing  in  carbon  trading.  These  strategies
ensure  that  only  authorized  participants  have  access  to  vital
information, thus enhancing the security and reliability of the
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

## 31072IEEE INTERNET OF THINGS JOURNAL, VOL. 12, NO. 15, 1 AUGUST 2025
data-sharing  process.  Leveraging  blockchain  technology,  all
transaction records remain immutable, which further reinforces
the  trust  framework.  Through  effective  permission  manage-
ment  and  key  collection,  we  uphold  the  confidentiality  and
integrity  of  data  within  a  dynamic,  distributed  environment.
This  not  only  supports  the  expansion  of  the  carbon  trading
market but also fosters increased confidence among stakehold-
ers, promoting wider participation.
## IV.  S
## ECURITYANALYSIS
Based on the proposed privacy protection mechanisms and
associated blockchain system components, the BCSM system
meets all security criteria as follows.
1)Enhanced Data Security:Our approach improves carbon
trading  data  security  by  storing  only  data  indices  on
the blockchain, avoiding direct storage of raw data. The
BCSM  system  uses  anonymous  private  keys  and  SPK
proofs to obscure sensitive information, ensuring secure
model exchanges and reducing data exposure risks.
2)Traceability  and  Legitimacy  Verification:The  BCSM
system enables tracing and verification of carbon trading
data.  Managers  can  link  anonymous  addresses  to  real
identities using certificates and smart contracts, ensuring
transaction legitimacy and fostering trust in the ecosys-
tem.
3)Decentralized  Trust  and  Data  Integrity:By  replacing
centralized data centers with decentralized trust entities
and  integrating  federated  learning  with  blockchain,  the
BCSM system enhances security. The HSDPS consensus
mechanism   selects   temporary   coordinators,   reducing
data breach risks and ensuring collaborative integrity.
Moreover,  since  carbon  trading  data  on  the  blockchain  is
signed with the owner’s private key, attackers cannot alter data
indices, ensuring data integrity and accountability. This cryp-
tographic protection fosters a secure, transparent environment,
enabling  confident  data  sharing  and  collaboration  in  carbon
trading initiatives.
## V.   P
## ERFORMANCEANALYSIS
In this section, we provide a comprehensive assessment of
the reliability and effectiveness of the proposed BCSM system
to validate the accuracy and integrity of its carbon trading data
model.  Our  evaluation  includes  a  series  of  experiments  and
simulations designed to test the system’s scalability, efficiency,
and overall performance in real-world scenarios.
Through  this  rigorous  testing  approach,  we  aim  to  under-
score  the  significant  advancements  achieved  by  our  BCSM
scheme  in  several  key  areas.  We  will  focus  on  the  efficiency
and  accuracy  of  the  carbon  trading  data  model,  showcas-
ing  how  our  system  enhances  data  integrity  and  reliability
through  blockchain’s  immutable  record-keeping  capabilities.
By   enabling   transparent   and   verifiable   data   transactions,
BCSM plays a crucial role in building stakeholder trust within
the carbon trading ecosystem.
## TA B L E  I
## C
## OMPARISON OF THECONTRIBUTIONPERCENTAGE FORDIFFERENT
## TYPES OFFEDERATEDLEARNING
A.  Data Description and Experimental Setting
In our research, we employed four key transportation carbon
emission datasets, each serving a vital role in our analysis. The
first dataset is the U.S. environmental protection agency (EPA)
motor  vehicle  emission  simulator  (MOVES),  which  provides
detailed information on emissions from various vehicle types
across  different  driving  conditions  in  the  United  States.  The
second dataset comes from the European environment agency
(EEA) and is part of the transport and environment reporting
mechanism (TERM), which offers insights into transportation-
related environmental impacts across Europe. Additionally, we
utilized the EEA TERM dataset again to ensure comprehensive
coverage  and  robustness  in  our  findings.  Lastly,  we  included
a  specific  transportation  carbon  emission  dataset  for  Beijing,
China,  which  spans  the  period  from  January  to  June  2022,
capturing recent emissions data in a major urban area known
for  its  transportation  challenges.  To  prepare  these  datasets
for  analysis,  we  conducted  a  thorough  data  preprocessing
procedure. This involved meticulous data cleaning to eliminate
inaccuracies  and  inconsistencies,  as  well  as  the  removal  of
outliers  that  could  skew  our  results.  By  implementing  these
preprocessing  steps,  we  were  able  to  ensure  that  the  data
adhered   to   the   stringent   requirements   of   our   information
sharing  model,  thereby  enhancing  the  reliability  and  validity
of our subsequent analyses and conclusions.
For  our  experiments,  we  utilized  the  Python  (3.7)  pro-
gramming   language   and   the   Scikit-learn   (Sklearn)   library
for  classification  modeling  and  data  partitioning.  PySyft  was
employed as the communication platform for federated learn-
ing.  The  CPU  used  in  these  experiments  was  an  Intel  Core
i7-6700K 4.00GHz.
B.  Comparison and Analysis of System Performance
TableIshows the percentage of contribution values obtained
from federated learning among the participants. The first three
rows represent cases where the local dataset was not attacked,
while  the  last  row  corresponds  to  a  scenario  where  there  are
four  data  providers,  and  the  dataset  of  the  last  data  provider
(D)was  subjected  to  an  attack  (in  this  scenario,  the  label
column values were reversed).
From  TableI,  it  is  evident  that  the  contribution  values  are
calculated as negative when nodes under attack are involved.
This highlights the robustness of our proposed BCSM training
mechanism in identifying compromised data sources.
In   summary,   our   proposed   BCSM   training   mechanism
ensures   efficient   and   accurate   carbon   trading   data   model
sharing without significantly increasing training time, thereby
demonstrating  superior  system  stability.  We  also  compared
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ENHANCED TRAFFIC CARBON EMISSIONS DATA SHARING AND MODELING31073
Fig. 5.Time comparison of federated learning types.
Fig. 6.Effect of gradients per user on running time.
the  performance  of  BCSM  across  two-party,  three-party,  and
four-party data providers under federated learning, where each
party  owns  a  portion  of  the  carbon  trading  data.  Data  users
can search the blockchain to identify and collaborate with the
relevant data owners for federated learning modeling.
In this study, four 64-bit Ubuntu 18 servers, each equipped
with 8 GB of RAM and 8-core CPUs, were used to assess the
performance of the proposed blockchain data storage method.
For  a  total  of  20  nodes,  each  machine  launched  five  Docker
containers  as  independent  blockchain  nodes.  A  test  chain
comprising  these  20  nodes  was  allowed  to  operate  for  one
hour  under  the  following  conditions:  each  node  sent  zero-
knowledge proof transactions every 10 s, while the other nodes
verified  and  packed  these  transactions  using  the  consensus
process.
As shown in Fig.5, when each party honestly contributes its
local  data  for  federated  learning,  the  trained  model  is  nearly
identical to one created by centralized federated training. The
primary  difference  lies  in  training  time:  as  the  number  of
participants increases, the communication overhead grows, and
federated  learning  becomes  more  computationally  intensive.
Consequently,  the  more  participants  involved  in  federated
learning, the longer the process takes.
## C.  Comparison With Other Methods
Fig.6compares  the  performance  of  our  proposed  BCSM
system  with  three  commonly  used  methods:  1)  MDL[38];
2) PPDL[39]; and 3) OFL[40]. As illustrated in Fig.6,the
total  time  grows  linearly  with  the  number  of  datasets.  When
the state is modified in BCSM, it takes approximately 10 s to
reach a consensus.
As  shown  in  Fig.6,  the  major  cost  is  incurred  when
invoking  a  contract  by  sending  a  transaction  on  the  BCSM
to  change  the  status  of  a  contract.  In  summary,  compared  to
existing approaches, our proposed BCSM training mechanism
Fig.  7.Interpretable  carbon  trading  data  characterization  and  experimental
results  of  the  blockchain-based  interpretable  carbon  trading  data  modeling
scheme BCSM.
Fig. 8.    Hierarchical smart contract HSDPS performance comparison results.
(a)  Throughput  of  layered  smart  contract  HSDPS  for  different  values  ofα.
(b)  Impact  of  Byzantine  nodes  on  time  consumption  under  layered  smart
contracts.
demonstrates  superior  performance.  Additionally,  under  the
same dropout rates and gradients per user metrics, our BCSM
method shows higher training success compared to other tech-
niques. Fig.7(a) illustrates the interpretable features output by
the blockchain-based interpretable carbon trading data model.
Fig.7(b) shows the Jaccard distance matrix among the carbon
trading data features selected over 50 iterations.
As  shown  in  Fig.8,  with  a  concurrency  of  500  nodes,
the  data  throughput  is  compared  across  different  numbers  of
nodes. The experimental results indicate that in a cluster with
varying node counts, the overall throughput of the hierarchical
smart  contract  algorithm  decreases  while  latency  increases
as  the  number  of  nodes  increases.  The  throughput  metric  is
relatively higher whenα=0.2, and atα=0.2orα=0.3, the
algorithm  exhibits  lower  latency.  Fig.8also  shows  that  as
the number of initial Byzantine nodes in the cluster increases,
the time required to convert a master node to a Byzantine node
decreases.
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

## 31074IEEE INTERNET OF THINGS JOURNAL, VOL. 12, NO. 15, 1 AUGUST 2025
## TA B L E  I I
## E
## XPERIMENTALRESULTS OFDIFFERENTALGORITHMS ONCARBONTRADINGDATA S E T  ATN=50
Fig. 9.Comparison of Byzantine time in carbon trading blockchain nodes.
To further assess the Byzantine fault tolerance performance
of the consensus algorithm within the carbon trading scheme,
a cluster of 16 nodes was configured, as shown in Fig.9.The
timing for the cluster to initiate a new round of primary node
election was evaluated under various distributions of Byzantine
nodes,  starting  from  the  moment  the  algorithm  commenced
operation. This timing is defined as the point when the primary
node  transitions  to  a  Byzantine  state  and  is  subsequently
identified as malicious by the system.
The results indicate that as the initial number of Byzantine
nodes in the cluster increases, the time required for the primary
node to transition into a Byzantine node decreases. Following
this, we conducted tests to measure the duration of the primary
node  elections,  comparing  these  results  with  those  from  the
consensus  algorithm’s  primary  node  election  experiments.  In
the proposed consensus algorithm, primary node elections are
carried out using a round-robin mechanism, where the rotation
of  nodes  designated  as  primary  nodes  is  recognized  as  a
successful election process by the cluster’s replica nodes.
Due to the hierarchical propagation and verification mecha-
nisms employed, the likelihood of proxy nodes (PB) becoming
Byzantine is relatively low, and these nodes maintain well-kept
local log entries. In contrast, the round-robin election method
used  in  the  PBFT  algorithm  fails  to  ensure  that  the  newly
elected  primary  node  is  a  reliable  one.  When  a  Byzantine
node  is  mistakenly  elected,  the  system  must  execute  a  new
round of view updates and primary node replacements. Thus,
the proposed consensus algorithm enhances the primary node
election  process  following  the  identification  of  a  malicious
primary node.
The  effectiveness  of  introducing  hierarchical  aggregation
mechanisms in personalized federated learning is further ana-
lyzed through experiments. In these experiments, we compared
the  average  accuracy  curves  of  the  hierarchical  aggregation
algorithm  with  our  proposed  method,  considering  the  intro-
duction  of  ID  and  Label.  We  will  compare  the  hierarchical
aggregation  algorithm  based  on  attention  mechanisms  and
hypernetworks  with  several  classical  federated  learning  algo-
rithms and recent advanced works. These benchmark methods
can be categorized into three groups.
1)Local   Training:Clients   train   solely   on   their   local
datasets without exchanging parameters. The final result
is obtained by averaging the performance evaluations of
all clients, denoted as Local.
2)TraditionalFederatedLearningAlgorithms:This
includes   the   classical   algorithms   FedAvg[41]and
FedProx[42].
3)Personalized   Federated   Learning:This   encompasses
FedBN[43],  FedROD[44],  pFedHN[45],  and  FedTP
## [46].
In  this  experiment,  three  Non-IID  partitioning  methods  were
simulated: 1) pat-balance; 2) pat-imbalance; and 3) dir. Their
definitions and simulation approaches are as follows.
1)pat-balance:Simulates  label  skew  across  clients.  Each
client  has  the  same  number  of  samples  and  labels,  but
the label categories differ between clients.
2)pat-imbalance:Simulates  both  label  skew  and  sample
quantity skew. Each client has the same number of label
categories,  but  the  specific  categories  and  local  dataset
sizes vary.
3)dir:Simulates  label  skew,  sample  quantity  skew,  and
varying  label  category  counts.  A  Dirichlet  distribution
(α=0.3)generates  a  label  distribution  matrix,  deter-
mining  the  labels  and  sampling  probabilities  for  each
client.  Samples  are  then  randomly  allocated  based  on
this matrix.
The experimental results are shown in TableIIand TableIII.
It  is  evident  that  the  optimized  embedding  vector  generation
method  converges  more  slowly,  as  the  hypernetwork  is  used
to  learn  the  similarities  of  the  same  label  between  different
clients.  This  approach  requires  a  finer  learning  granularity
compared   to   the   method   in   pFedHN,   necessitating   more
rounds to complete the information-sharing process. However,
the  overall  modeling  efficiency  remains  within  a  satisfactory
range, providing effective support for efficient carbon trading
data sharing.
The experimental analysis in Fig.10shows that the impact
of the number of clients on the performance of the algorithms
does  not  exhibit  a  uniform  trend  across  all  methods.  This
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ENHANCED TRAFFIC CARBON EMISSIONS DATA SHARING AND MODELING31075
## TABLE III
## E
## XPERIMENTALRESULTS OFDIFFERENTALGORITHMS ONCARBONTRADINGDATA S E T  ATN=100
variation  is  likely  due  to  two  factors:  first,  the  increase  in
the  number  of  clients  leads  to  a  larger  overall  data  volume;
second, the influence of Non-IID data implies greater diversity
in  data  distribution  and  model  parameter  update  directions.
These  factors  present  a  significant  challenge  for  the  server
when aggregating parameters.
To   further   validate   the   effectiveness   of   the   proposed
mechanisms—reallocating  computational  resources  from  less
important   hyperparameters   to   more   critical   ones   and   the
dual-stage   approach   that   optimizes   the   feature   extraction
process  while  enhancing  the  overall  learning  efficacy  of  the
framework–we conducted experiments to evaluate their impact
on  training  performance.  The  experiments  were  carried  out
in  federated  learning  environments  with  N=20,  30,  and  40
nodes,  respectively.  For  each  scenario,  the  training  process
was  repeated  50  times,  and  the  average  values  of  Accuracy
and  AUC  were  calculated  for  comparison.  Here,  Pre  denotes
the  baseline  training  without  employing  either  the  reallo-
cating  computational  resources  mechanism  or  the  dual-stage
approach,  while  Post-RC  and  Post-DA  represent  the  train-
ing with the reallocating computational resources mechanism
and  the  dual-stage  approach,  respectively.  TableIVpresents
the  performance  comparison  before  and  after  applying  these
mechanisms.
The results in TableIVdemonstrate that reallocating com-
putational  resources  from  less  important  hyperparameters  to
more   critical   ones   significantly   improves   performance   by
prioritizing  and  preserving  more  impactful  hyperparameters.
Additionally,  the  dual-stage  approach  effectively  enhances
the  model’s  training  efficiency  while  optimizing  the  feature
extraction process. These findings confirm the effectiveness of
both  mechanisms  in  improving  the  overall  performance  and
efficiency of the framework.
In  summary,  based  on  the  analysis  of  the  experimental
results,  the  proposed  personalized  federated  learning  method
consistently  demonstrates  optimal  performance  across  nearly
all   scenarios.   Moreover,   the   method   exhibits   a   relatively
smooth  trend  in  response  to  changes  in  the  degree  of  Non-
IID  and  the  number  of  clients,  indicating  better  robustness
compared  to  baseline  methods.  Therefore,  the  experimental
results  validate  the  effectiveness  of  our  proposed  method
for  handling  Non-IID  carbon  trading  data  between  clients
while  maintaining  good  scalability.  The  experiments  demon-
strate  that  leveraging  automated  machine  learning  models
provides  a  more  efficient  approach  for  developing  carbon
trading  price  prediction  models.  This  efficiency  stems  from
the substantial influence of time-series data volume on carbon
Fig.  10.Comparison  of  the  accuracy  curves  of  the  proposed  personalized
federated learning approach and the baseline approach. (a) Average accuracy
curves  underN=50  and  pat-balance.  (b)  Average  accuracy  curves  under
N=100  and  pat-balance.  (c)  Average  accuracy  curves  underN=50  and  pat-
imbalance. (d) Average accuracy curves underN=100 and pat-imbalance.
emission trading and the complexity of model construction on
predictive accuracy. By integrating the precise search capabil-
ities of federated learning with data augmentation techniques
to  broaden  data  scope,  our  method  ensures  optimal  model
selection  within  the  search  space  while  significantly  improv-
ing  the  performance  of  the  final  carbon  trading  prediction
model.
The  growth  trend  of  the  average  accuracy  of  both  the
benchmark  method  and  our  proposed  method  is  depicted
as  the  number  of  communication  rounds  increases,  using
datasets from carbon trading with varying numbers of clients
and  partitioning  methods.  By  observing  the  plots,  we  notice
that  the  accuracy  curves  of  the  federated  learning  algorithms
exhibit  oscillations.  This  is  primarily  due  to  Non-IID  data
among  the  clients,  which  leads  to  different  update  directions
in  local  models.  After  each  aggregation,  some  client  models
are  negatively  impacted,  resulting  in  an  oscillating  upward
trend.  As  the  degree  of  Non-IID  increases,  and  client  model
update  biases  grow,  this  oscillation  phenomenon  intensifies.
The  curves  of  the  local  models  are  smoother  and  converge
faster because they are not aggregated and thus unaffected by
client bias; however, their final performance is notably inferior
to that of the personalized federated learning methods.
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

## 31076IEEE INTERNET OF THINGS JOURNAL, VOL. 12, NO. 15, 1 AUGUST 2025
## TA B L E  I V
## C
OMPARISON OF THEPERFORMANCECOMPARISONBEFORE ANDAFTERAPPLYINGREALLOCATINGCOMPUTATIONAL
## RESOURCESMETHOD ANDDUAL-STAG EAPPROACH
Fig. 11.    Comparative results on the effectiveness of introducing hierarchical
aggregation mechanisms in personalized federated learning.
By comparing all the curves in Fig.10, it becomes evident
that personalized federated learning algorithms perform signif-
icantly  better  in  Non-IID  scenarios  than  traditional  federated
learning methods. The average accuracy curves of the method
proposed  in  this  article  exhibit  a  similar  behavior  under  six
different settings, with fewer variations in oscillation and faster
convergence  compared  to  the  baseline  methods.  Therefore,
it  can  be  concluded  that  the  proposed  method  demonstrates
superior robustness.
The  effectiveness  of  introducing  hierarchical  aggregation
mechanisms   in   personalized   federated   learning   is   further
analyzed  through  experiments,  specifically  in  the  context  of
incorporating  carbon  trading  data  ID  and  Label.  The  exper-
imental  results,  shown  in  Fig.11,  reveal  that  the  optimized
embedding vector generation method converges more slowly.
This slower convergence  occurs because the hypernetwork is
used  to  learn  similar  information  for  the  same  label  across
different  clients,  resulting  in  finer  learning  granularity  com-
pared  to  the  method  in  pFedHN.  Consequently,  more  rounds
are  required  to  complete  this  information-sharing  process.
Nonetheless,  the  overall  modeling  efficiency  remains  within
a  satisfactory  range,  providing  effective  support  for  efficient
carbon trading data sharing.
## VI.  C
## ONCLUSION ANDFUTUREWORK
Efficient  sharing  and  modeling  of  traffic  carbon  emissions
data  are  vital  for  advancing  the  IIoT  ecosystem  and  pro-
moting  sustainable  energy  solutions.  To  address  challenges
such   as   data   privacy,   cross-platform   sharing,   and   access
control,  we  propose  BCSM—a  blockchain-based  framework
integrating secure data storage, personalized federated learning
for  privacy-preserving  collaborative  training,  and  an  efficient
access  control  system.  This  approach  enhances  data  security,
facilitates seamless collaboration, and ensures regulatory com-
pliance,  supporting  effective  carbon  management  and  energy
transition initiatives.
However, limitations remain in privacy protection and trans-
action  efficiency.  Future  research  will  focus  on  enhancing
privacy  through  advanced  encryption  techniques  like  homo-
morphic encryption and optimizing the blockchain consensus
mechanism,  such  as  proof-of-stake,  to  improve  transaction
speed  and  scalability.  These  improvements  aim  to  strengthen
the BCSM framework, making it more robust and suitable for
global implementation in energy transition efforts.
## R
## EFERENCES
[1]   X.  Xia,  X.  Zeng,  W.  Wang,  C.  Liu,  and  X.  Li,  “Carbon  constraints
and  carbon  emission  reduction:  An  evolutionary  game  model  within
the  energy-intensive  sector,”Expert  Syst.  Appl.,  vol.  244,  Jun.  2024,
Art. no. 122916.
[2]   J.-T.  Hong,  Y.-L.  Bai,  Y.-T.  Huang,  and  Z.-R.  Chen,  “Hybrid  carbon
price   forecasting   using   a   deep   augmented   FEDformer   model   and
multimodel optimization piecewise error correction,”Expert Syst. Appl.,
vol. 247, Aug. 2024, Art. no. 123325.
[3]   Y.  Niu,  Y.  Han,  Y.  Li,  M.  Zhang,  and  H.  Li,  “Low–carbon  regulation
method  for  greenhouse  light  environment  based  on  multi–objective
optimization,”Expert Syst. Appl., vol. 252, Oct. 2024, Art. no. 124228.
[4]   S.  Wang,  X.  Zhang,  J.  Peng,  Y.  Tan,  and  Z.  Fan,  “Providing  solutions
for carbon emission reduction using the TOE framework,”Expert Syst.
Appl., vol. 255, Dec. 2024, Art. no. 124547.
[5]   M.  Kouhizadeh  and  J.  Sarkis,  “Blockchain  practices,  potentials,  and
perspectives in greening supply chains,”Sustainability, vol. 10, no. 10,
p. 3652, 2018.
[6]   Y.  Xu  et  al.,  “A  blockchain-based  framework  for  carbon  management
towards   construction   material   and   product  certification,”Adv.   Eng.
Inform., vol. 61, Aug. 2024, Art. no. 102242.
[7]   P.  Kairouz  et  al.,  “Advances  and  open  problems  in  federated  learn-
ing,”Found. Trends
## R
## 
Mach. Learn., vol. 14, nos. 1–2, pp. 1–210, 2021.
[8]   M.  Parhamfar,  I.  Sadeghkhani,  and  A.  M.  Adeli,  “Towards  the  net
zero carbon future: A review of blockchain-enabled peer-to-peer carbon
trading,”Energy Sci. Eng., vol. 12, no. 3, pp. 1242–1264, 2024.
[9]   Z. Hu, Y. Du, C. Rao, and M. Goh, “Delegated proof of reputation con-
sensus  mechanism  for  blockchain-enabled  distributed  carbon  emission
trading system,”IEEE Access, vol. 8, pp. 214932–214944, 2020.
[10]  N.  Rieke  et  al.,  “The  future  of  digital  health  with  federated  learn-
ing,”NPJ Digit. Med., vol. 3, no. 1, pp. 1–7, 2020.
[11]  X.-Q.  Chen,  C.-Q.  Ma,  Y.-S.  Ren,  and  Y.-T.  Lei,  “Carbon  allowance
auction  design  of  china’s  ETS:  A  comprehensive  hierarchical  system
based  on  blockchain,”Int.  Rev.  Econ.  Finan.,  vol.  88,  pp. 1003–1019,
## Nov. 2023.
[12]  A. Al Sadawi, B. Madani, S. Saboor, M. Ndiaye, and G. Abu-Lebdeh,
“A  comprehensive  hierarchical  blockchain  system  for  carbon  emission
trading  utilizing  blockchain  of  things  and  smart  contract,”Technol.
Forecast. Soc. Change, vol. 173, Dec. 2021, Art. no. 121124.
[13]  M.-K.  Kazi  and  M.  M.  F.  Hasan,  “Optimal  and  secure  peer-to-peer
carbon   emission   trading:   A   game   theory   informed   framework   on
blockchain,”Comput. Chem. Eng., vol. 180, Jan. 2024, Art. no. 108478.
[14]  T.-y.  Zhang,  T.-t.  Feng,  and  M.-l.  Cui,  “Smart  contract  design  and
process  optimization  of  carbon  trading  based  on  blockchain:  The  case
of China’s electric power sector,”J. Clean. Prod., vol. 397, Apr. 2023,
Art. no. 136509.
[15]  D.   Ressi,   R.   Romanello,   C.   Piazza,   and   S.   Rossi,   “AI-enhanced
blockchain technology: A review of advancements and opportunities,”J.
Netw. Comput. Appl., vol. 225, May 2024, Art. no. 103858.
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ENHANCED TRAFFIC CARBON EMISSIONS DATA SHARING AND MODELING31077
[16]  M.  Zhaofeng,  W.  Xiaochang,  D.  K.  Jain,  H.  Khan,  G.  Hongmin,  and
W. Zhen, “A blockchain-based trusted data management scheme in edge
computing,”IEEE Trans. Ind. Informat., vol. 16, no. 3, pp. 2013–2021,
## Mar. 2020.
[17]  Y. Qu, S. R. Pokhrel, S. Garg, L. Gao, and Y. Xiang, “A blockchained
federated  learning  framework  for  cognitive  computing  in  industry  4.0
networks,”IEEE  Trans.  Ind.  Informat.,  vol.  17,  no.  4,  pp. 2964–2973,
## Apr. 2021.
[18]  L.  Xu,  T.  Bao,  and  L.  Zhu,  “Blockchain  empowered  differentially
private and auditable data publishing in industrial IoT,”IEEE Trans. Ind.
Informat., vol. 17, no. 11, pp. 7659–7668, Nov. 2021.
[19]  C. Zhang, Y. Xie, H. Bai, B. Yu, W. Li, and Y. Gao, “A survey on feder-
ated learning,”Knowl.-Based Syst., vol. 216, Mar. 2021, Art. no. 106775.
[20]  S.  AbdulRahman,  H.  Tout,  H.  Ould-Slimane,  A.  Mourad,  C.  Talhi,
and  M.  Guizani,  “A  survey  on  federated  learning:  The  journey  from
centralized  to  distributed  on-site  learning  and  beyond,”IEEE  Internet
Things J., vol. 8, no. 7, pp. 5476–5497, Apr. 2021.
[21]  V.  Mothukuri,  R.  M.  Parizi,  S.  Pouriyeh,  Y.  Huang,  A.  Dehghantanha,
and G. Srivastava, “A survey on security and privacy of federated learn-
ing,”Future Gener. Comput. Syst., vol. 115, pp. 619–640, Feb. 2021.
[22]  L. U. Khan, W. Saad, Z. Han, E. Hossain, and C. S. Hong, “Federated
learning   for   Internet   of   Things:   Recent   advances,   taxonomy,   and
open   challenges,”IEEE   Commun.   Surveys   Tuts.,   vol.   23,   no.   3,
pp. 1759–1799, 3rd Quart., 2021.
[23]  R.  Ye,  M.  Xu,  J.  Wang,  C.  Xu,  S.  Chen,  and  Y.  Wang,  “FedDisco:
Federated learning with discrepancy-aware collaboration,” inProc. 40th
Int. Conf. Mach. Learn., 2023, pp. 39879–39902.
[24]  X.   Chang   et   al.,   “The   coupling   effect   of   carbon   emission   trad-
ing   and   tradable   green   certificates   under   electricity   marketization
in   China,”Renew.   Sustain.   Energy   Rev.,   vol.   187,   Nov.   2023,
Art. no. 113750.
[25]  Y.  Zhang,  S.  Li,  T.  Luo,  and  J.  Gao,  “The  effect  of  emission  trading
policy on carbon emission reduction: Evidence from an integrated study
of  pilot  regions  in  China,”J.  Clean.  Prod.,  vol.  265,  Aug.  2020,
Art. no. 121843.
[26]  X.  Yang,  P.  Jiang,  and  Y.  Pan,  “Does  China’s  carbon  emission  trading
policy have an employment double dividend and a porter effect?”Energy
Policy, vol. 142, Jul. 2020, Art. no. 111492.
[27]  Y.  Huang  and  Z.  He,  “Carbon  price  forecasting  with  optimization
prediction   method   based   on   unstructured   combination,”Sci.   Total
Environ., vol. 725, Jul. 2020, Art. no. 138350.
[28]  W. Sun and C. Huang, “A novel carbon price prediction model combines
the secondary decomposition algorithm and the long short-term memory
network,”Energy, vol. 207, Sep. 2020, Art. no. 118294.
[29]  X. Pan, M. Li, H. Xu, S. Guo, R. Guo, and C. T. Lee, “Simulation on
the effectiveness of carbon emission trading policy: A system dynamics
approach,”J. Oper. Res. Soc., vol. 72, no. 7, pp. 1447–1460, 2021.
[30]  Q.  An,  K.  Zhu,  B.  Xiong,  and  Z.  Shen,  “Carbon  resource  reallocation
with  emission  quota  in  carbon  emission  trading  system,”J.  Environ.
Manag., vol. 327, Feb. 2023, Art. no. 116837.
[31]  Y.-y.  Chi,  H.  Zhao,  Y.  Hu,  Y.-k.  Yuan,  and  Y.-x.  Pang,  “The  impact
of  allocation  methods  on  carbon  emission  trading  under  electricity
marketization  reform  in  China:  A  system  dynamics  analysis,”Energy,
vol. 259, Nov. 2022, Art. no. 125034.
[32]  A. Muzumdar, C. Modi, and C. Vyjayanthi, “A permissioned blockchain
enabled trustworthy and incentivized emission trading system,”J. Clean.
Prod., vol. 349, May 2022, Art. no. 131274.
[33]  S.  Guo,  X.  Hu,  S.  Guo,  X.  Qiu,  and  F.  Qi,  “Blockchain  meets  edge
computing:  A  distributed  and  trusted  authentication  system,”IEEE
Trans. Ind. Informat., vol. 16, no. 3, pp. 1972–1983, Mar. 2020.
[34]  H. Lin, S. Garg, J. Hu, G. Kaddoum, M. Peng, and M. S. Hossain, “A
blockchain-based secure data aggregation strategy using sixth generation
enabled  network-in-box  for  industrial  applications,”IEEE  Trans.  Ind.
Informat., vol. 17, no. 10, pp. 7204–7212, Oct. 2021.
[35]  Y.  Tan,  J.  Liu,  and  N.  Kato,  “Blockchain-based  key  management  for
heterogeneous  flying  ad  hoc  network,”IEEE  Trans.  Ind.  Informat.,
vol. 17, no. 11, pp. 7629–7638, Nov. 2021.
[36]  L.  Witt,  M.  Heyer,  K.  Toyoda,  W.  Samek,  and  D.  Li,  “Decentral
and incentivized federated learning frameworks: A systematic literature
review,”IEEE   Internet   Things   J.,   vol.   10,   no.   4,   pp. 3642–3663,
## Feb. 2022.
[37]  S.  Liu,  H.  Zhang,  and  Y.  Jin,  “A  survey  on  computationally  efficient
neural  architecture  search,”J.  Autom.  Intell.,  vol.  1,  no.  1,  2022,
Art. no. 100002.
[38]  F. Tramer and D. Boneh, “Slalom: Fast, verifiable and private execution
of neural networks in trusted hardware,” 2019,arXiv:1806.03287.
[39]  L.  T.  Phong,  Y.  Aono,  T.  Hayashi,  L.  Wang,  and  S.  Moriai,  “Privacy-
preserving  deep  learning:  Revisited  and  enhanced,”  inProc.  8th  Int.
Conf. Appl. Techn. Inf. Secur., 2017, pp. 100–110.
[40]  G.  Xu,  H.  Li,  S.  Liu,  K.  Yang,  and  X.  Lin,  “VerifyNet:  Secure
and  verifiable  federated  learning,”IEEE  Trans.  Inf.  Forensics  Security,
vol. 15, pp. 911–926, 2020.
[41]  B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y. Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” inProc. 20th Int. Conf. Artif. Intell. Statist., 2017, pp. 1273–1282.
[42]  T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated  optimization  in  heterogeneous  networks,”  inProc.  Mach.
Learn. Syst., 2020, pp. 429–450.
[43]  X. Li, M. Jiang, X. Zhang, M. Kamp, and Q. Dou, “FedBN: Federated
learning  on  non-IID  features  via  local  batch  normalization,”  2021,
arXiv:2102.07623.
[44]  H.-Y.  Chen  and  W.-L.  Chao,  “On  bridging  generic  and  personalized
federated learning for image classification,” 2022,arXiv:2107.00778.
[45]  A.  Shamsian,  A.  Navon,  E.  Fetaya,  and  G.  Chechik,  “Personalized
federated learning using hypernetworks,” inProc. 38th Int. Conf. Mach.
Learn., 2021, pp. 9489–9502.
[46]  H.  Li  et  al.,  “FedTP:  Federated  learning  by  transformer  personal-
ization,”IEEE  Trans.  Neural  Netw.  Learn.  Syst.,  vol.  35,  no.  10,
pp. 13426–13440, Oct. 2024.
Xinhuan Zhangreceived the Ph.D. degree in trans-
portation  planning  and  management  from  Tongji
University, Shanghai, China, in 2012.
She   has   been   an   Assistant   Professor   and   a
Master’s  Advisor  with  the  Institute  of  Road  and
Transportation,  College  of  Engineering,  Zhejiang
Normal University, Jinhua, China, since May 2012,
specializes  in  evaluating  and  predicting  intelligent
public  transportation  systems,  travel  time  forecast-
ing,  and  researching  connected  automated  vehicle
highway  systems.  With  over  a  decade  of  expertise,
she  has  actively  contributed  to  national  projects  funded  by  the  Zhejiang
Provincial  Natural  Science  Foundation  and  collaborated  with  enterprises  on
innovative transportation initiatives. Her academic portfolio features over 35
publications  in  leading  journals,  five  of  which  are  SCI  highly  cited,  along
with two invention patents applied in regional intelligent transportation pilot
projects.  Committed  to  bridging  theory  and  practice,  she  mentors  master’s
students in fields like vehicle-road collaboration simulation and advocates for
sustainable  mobility  through  educational  outreach  and  industry  partnerships,
focusing on areas such as CAV test scenario design, transportation infrastruc-
ture upgrading, and open big data platform development.
Hongjie  Liureceived  the  Ph.D.  degree  in  com-
puter   science   and   technology   from   the   School
of   Electronic   Science   and   Engineering,   Faculty
of  Electronic  and  Information  Engineering,  Xi’an
Jiaotong University, Xi’an, China, in 2024.
He  was  a  Visiting  Scholar  with  the  University
of   Wisconsin,   Madison,   WI,   USA.   His   primary
research focuses on artificial intelligence, intelligent
transportation,  and  autonomous  driving.  In  these
domains,  he  has   authored/co-authored  dozens  of
related  papers  and  led  or  participated  in  several
scientific research projects.
Fan Yangreceived the Ph.D. degree in computer sci-
ence and technology from Xi’an Jiaotong University,
Xi’an, China, in 2023.
He   is   currently   an   Assistant   Professor   with
the  School  of  Computer  Science  and  Technology,
Xi’an Jiaotong University. He simultaneously holds
the  Distinction  of  a  Distinguished  Professor  with
Xi’an  Jiaotong  University  Suzhou  Academy.  He  is
intensively immersed in research activities centered
around  blockchain,  AIGC  security,  and  associated
domains,  actively  engaging  in  the  dissemination  of
projects at both national and international levels.
Authorized licensed use limited to: Viet Nam National University Ho Chi Minh City. Downloaded on January 31,2026 at 13:20:45 UTC from IEEE Xplore.  Restrictions apply.