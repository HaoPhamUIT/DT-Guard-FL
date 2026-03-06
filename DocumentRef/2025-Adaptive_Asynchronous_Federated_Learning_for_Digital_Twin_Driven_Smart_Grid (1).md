

## IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 20254167
Adaptive Asynchronous Federated Learning for
## Digital Twin Driven Smart Grid
Zhuoqun Zhang, Haipeng Peng, Lixiang Li, and Shuang Bao
Abstract—The smart grid represents a revolutionary advance-
ment,   ushering   power   systems   into   an   era   of   enhanced
intelligence.   Unlike   traditional   power   networks,   smart   grids
demand superior real-time performance, security, and accuracy.
However, their development faces significant challenges, including
delays  in  device  status  updates,  malicious  station  attacks,  and  a
lack  of  user  trust,  which  impede  service  quality  improvements.
To address these issues, this paper proposes a Privacy-Preserving
Smart Grid distributed Collaborative computing system (PPSG)
that  integrates  blockchain  and  asynchronous  federated  learning
technologies. A digital twin framework tailored for smart grids is
designed, enabling real-time simulation and reflection of electrical
devices’ states and behaviors, thereby enhancing service respon-
siveness. Additionally, to tackle non-independent and identically
distributed  (Non-IID)  data  and  outdated  local  models,  a  dual
dynamic   aggregation   factor   asynchronous   federated   learning
scheme  is  introduced,  improving  service  accuracy.  The  “Proof
of Contribution” blockchain consensus algorithm is employed to
assess  contributions  to  computational  tasks  and  utilize  stochas-
tic  processes  to  mitigate  election  fraud,  thereby  strengthening
security. Extensive comparative experiments on Non-IID datasets
and heterogeneous devices demonstrate PPSG’s superior learning
performance,   efficiency,   and   reliability.   Furthermore,   experi-
ments   using   real   power   grid   datasets   validate   its   practical
applicability,  scalability  in  large-scale  node  environments,  and
feasibility for  real-world  deployment.
Index   Terms—Smart   grid,   digital   twin,   blockchain,   asyn-
chronous  federated  learning,  privacy-preserving  computing.
## I.  INTRODUCTION
## I
N  RECENT  years,  the  power  grid,  as  a  crucial  civil-
ian  infrastructure,  has  been  advancing  towards  integrating
advanced  communication,  information,  and  control  technolo-
gies.  Smart  grid  featuring  state  monitoring,  fault  analysis,
and  automatic  decision-making  have  become  the  mainstream
trend[1].  However,  the  complex  and  heterogeneous  nature
of  electrical  devices,  combined  with  the  dynamic  power  grid
environment,  poses  significant  challenges  for  current  smart
Received 19 August 2024; revised 21 January 2025; accepted 10 June 2025.
Date of publication 13 June 2025; date of current version 25 August 2025. This
work was supported in part by the National Key R&D Program of China under
Grant 2020YFB1805403; in part by the National Natural Science Foundation
of China under Grant 62032002; and in part by the 111 Project under Grant
B21049. Paper no. TSG-01422-2024.(Corresponding author: Haipeng Peng.)
The   authors   are   with   the   Information   Security   Center,   State   Key
Laboratory  of  Networking  and  Switching  Technology,  and  the  National
Engineering Laboratory for Disaster Backup and Recovery, Beijing University
of  Posts  and  Telecommunications,  Beijing  100876,  China  (e-mail:  zhuo-
qun.zhang@bupt.edu.cn;    penghaipeng@bupt.edu.cn;    lixiang@bupt.edu.cn;
icebear@bupt.edu.cn).
Color  versions  of  one  or  more  figures  in  this  article  are  available  at
https://doi.org/10.1109/TSG.2025.3579492.
Digital Object Identifier 10.1109/TSG.2025.3579492
grid to consistently provide accurate fault analysis and efficient
operational decisions[2].
Digital  twin  (DT)  technology,  which  integrates  physical
sensors, machine learning (ML), software analytics, and spatial
modeling,  has  emerged  as  a  promising  approach  to  create
real-time  virtual  simulations  of  physical  systems,  effectively
capturing   the   dynamic   and   complex   power   grid   environ-
ment[3].  By  predicting  future  events  and  enabling  control
through multi-source data learning, DT transforms the state of
electrical  devices,  facilitating  bidirectional  closed-loop  feed-
back[4].  Its  superior  state  awareness  and  real-time  analysis
capabilities  are  crucial  for  operational  decision-making  and
execution.
However, data silos and privacy concerns in power grid con-
strain  large-scale  centralized  learning,  thereby  impeding  the
development  of  DT  technology  within  smart  grid.  Federated
learning  (FL),  as  a  distributed  ML  framework,  trains  models
using  client-side  local  data,  enabling  collaborative  training
among  different  entities  while  overcoming  data  silos[5].In
smart  grid,  the  heterogeneous  computation  capabilities  and
data   distribution   of   electrical   devices   significantly   impact
FL  performance.  Although  asynchronous  federated  learning
(AFL)  is  typically  used  to  enhance  efficiency  by  reducing
the  straggler  effect[6],  high  aggregation  frequency  and  non-
independent  and identically distributed (Non-IID) data in the
power grid lead to unstable AFL performance.
Moreover, while blockchain technology has been employed
to enhance the security and trustworthiness of FL, making the
training  process  more  decentralized  and  transparent[7],the
consensus  process  remains  time-consuming,  especially  with
computation-intensive  (e.g.,  PoW)[8]and  communication-
intensive   (e.g.,   PBFT)[9]consensus   algorithms.   Existing
committee-based  consensus  algorithms  (e.g.,  DPoS)  improve
efficiency  but  pose  centralization  risks,  making  them  less
suitable for power grid scenarios[10].
Research  Gaps  and  Motivation:Despite  advancements,
significant   challenges   remain   in   integrating   DT,   FL,   and
blockchain technologies into smart grid:
•Current  DT  applications  in  smart  grid  are  hindered  by
data heterogeneity, privacy concerns, and lack of efficient
distributed learning mechanisms.
•Existing  AFL  schemes  do  not  simultaneously  address
outdated local models and Non-IID data, leading to poor
learning efficiency and quality in power grid.
•Blockchain-enhanced  FL  frameworks  often  suffer  from
high  consensus  overhead  and  centralization  risks,  which
are not thoroughly addressed in the context of smart grid.
## 1949-3053
c
2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies.  Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4168IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
Contributions:To address these gaps, this paper introduces
a privacy-preserving smart grid distributed collaborative com-
puting system (PPSG) that integrates DT, AFL, and blockchain
technologies. The key contributions are:
•An  adaptive  AFL  scheme  driven  by  DT  for  smart  grid,
delivering  real-time  monitoring,  robust  fault  diagnosis,
and  efficient  resource  management,  thereby  reinforcing
operational   stability,   enhancing   data-driven   decision-
making,  and  ensuring  a  scalable,  resilient  infrastructure
for modern power system.
•A  dual  dynamic  aggregation  factor,  designed  to  assign
appropriate  weights  to  local  models  based  on  local  data
distribution and model timeliness, enabling more accurate
and robust AFL convergence.
•A  novel  contribution-based  consensus  algorithm,  which
assesses the contributions of stations to computing tasks,
mitigates  poisoning  attacks,  reduces  election  fraud  risk
through  stochastic  processes,  and  ensures  secure  global
model   aggregation   in   the   blockchain-enhanced   AFL
framework.
The  rest  of  the  paper  is  organized  as  follows:  SectionII
reviews related work. SectionIIIdescribes the system architec-
ture and aggregation process. SectionIVdetails the modeling
of the AFL scheme with the dual dynamic aggregation factor
and the contribution-based weighting stochastic election algo-
rithm. SectionVpresents comparative experiments evaluating
the proposed scheme. SectionVIconcludes the paper.
## II.  R
## ELATEDWORK
The  proposed  PPSG  integrates  blockchain  and  AFL  tech-
nologies,  embedded  within  the  DT  of  the  smart  grid.  The
related  work  is  divided  into  three  sections:  1)  DT  and  smart
grid; 2) FL and AFL; 3) blockchain-enhanced technologies.
A.  Digital Twin and Smart Grid
As an advanced digital technology, DT plays a pivotal role
in  constructing  and  optimizing  smart  grid[3].  By  creating
high-fidelity  virtual  models  of  physical  smart  grid  system,
DT  facilitates  real-time  monitoring,  dynamic  simulation,  and
predictive  maintenance  of  various  grid  components[4].In
distributed  photovoltaic  systems,  DT  enables  fault  diagno-
sis  by  predicting  potential  failures  and  reducing  the  risk
of  power  outages[11].  Moutis  and  Alizadeh-Mousavi[12]
designed   a   DT   model   for   the   medium   voltage   side   of
transformers,  achieving  real-time  monitoring  of  distribution
grid  systems.  Xiao  et  al.[13]developed  a  DT-based  grid
time  series  forecasting  algorithm,  enabling  the  prediction  of
future  power  grid  operations  and  the  timely  implementation
of  corresponding  measures.  Furthermore,  Zhang  et  al.[14]
presented   DT-based   robust   residual   observer   models   that
provide primary active fault-tolerant control strategies, enhanc-
ing  power  distribution  accuracy,  transient  response  speed,
and  system  robustness.  These  advancements  optimize  oper-
ational  efficiency,  improve  system  reliability,  and  promote
sustainable  development,  underscoring  DT’s  significance  as
a  cornerstone  for  the  future  evolution  of  intelligent  power
systems.
Nevertheless, the application of DT in smart grid is still in
its infancy and faces major challenges, such as heterogeneous
information,  the  existence  of  information  islands,  and  non-
uniform data and model platforms.
B.  Federated Learning and Asynchronous Federated
## Learning
FL  is  a  rapidly  growing  paradigm  focused  on  enhancing
data  privacy  by  training  models  locally,  thereby  minimizing
data leakage risks[15],[16],[17]. Traditional FL algorithms,
like  FedAvg[5],  use  synchronous  architectures,  aggregating
local  updates  via  SGD  on  a  central  server.  Yang  et  al.[18]
proposed an electricity theft detection model based on a multi-
view broad learning system, enhancing the detection accuracy
of high-dimensional imbalanced electricity data. FedProx[19]
and  FedAdam[20]optimize  this  process  by  incorporating
proximal terms and adaptive methods to enhance global model
convergence.   Chen   et   al.[21],[22]proposed   multi-client
selection strategies along with privacy protection mechanisms
to effectively address issues of low training accuracy and pri-
vacy leakage. However, synchronous methods are constrained
by the slowest node’s pace. In resource-heterogeneous power
grid, AFL[23],[24],[25]is used to reduce aggregation delays
and  enhance  efficiency,  with  approaches  like  FedAsync[26]
mitigating the straggler effect. KAFL[27]further refines AFL
by dynamically adjusting weights based on client contribution.
Whereas, most of the existing AFL schemes does not con-
sider the scenarios of outdated local models and Non-IID data
simultaneously,  which  leads  to  poor  learning  efficiency  and
quality in the power grid. In complex smart grid environment,
assigning appropriate weights to local models and improving
the  reliability  of  the  power  grid  are  crucial  for  enhancing
service quality.
C.  Blockchain-Enhanced Technology
Blockchain   is   a   decentralized   ledger   technology   ensur-
ing  data  immutability  and  authenticity  through  cryptographic
methods[15],[23].  Its  inherent  decentralization  and  trans-
parency   have   been   extensively   applied   within   smart   grid
[28],  significantly  enhancing  data  security  and  the  efficiency
of  energy  transactions,  thereby  fostering  the  intelligent  and
sustainable   management   of   energy[29].   Barbhaya   et   al.
[30]proposed the blockchain-based ETradeChain platform to
improve  the  decentralized  energy  trading  efficiency  of  the
local  energy  market  in  the  smart  grid.  Jiang  et  al.[31]
designed a blockchain-based privacy-preserving energy trading
mechanism,  which  solves  the  privacy  leakage  problem  in
decentralized energy trading systems through covert on-chain
transmission. Several studies have integrated blockchain with
FL  to  enhance  the  security  and  transparency  of  the  model
training process[32],[33],[34]. Shayan et al.[35]optimized
FL using blockchain and cryptographic primitives, effectively
defending  against  poisoning  attacks.  Veerasamy  et  al.[36]
developed a blockchain-based FL framework regulating energy
transaction supply and demand via smart contracts. Xu et al.
[37]introduced  DBAFL,  an  AFL  scheme  with  a  dynamic
blockchain-based scaling factor.
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4169
However,  these  schemes  do  not  simultaneously  address
efficiency,   reliability,   and   potential   election   fraud   issues.
Therefore,  designing  a  secure  consensus  algorithm  incorpo-
rating DT technology  to meet  the high  real-time demands  of
smart grid is of great significance.
## III.  S
## YSTEMMODEL
This  section  elaborates  on  the  PPSG  model  from  the  per-
spectives of system architecture, DT modeling, and workflow.
## A.  Architecture Overview
The proposed architecture, illustrated in Fig.1, consists of
three  layers:  device  layer,  blockchain  layer,  and  DT  layer
(digital twin layer).
Device Layer:This layer manages data sensing, collection,
transmission, and local model training. The power grid system,
encompassing generation (e.g., hydroelectric, nuclear, thermal
plants),  transmission  (e.g.,  high-voltage  lines,  substations),
distribution (e.g., lines, transformers), and consumption (e.g.,
residential, industrial, commercial), along with associated sen-
sors, networks, storage, and computational devices, forms the
device layer. Independent stations, such as substations, power
plants,  factories,  or  households,  host  various  devices  (e.g.,
sensors,  cameras,  meters)  that  store  data  through  their  asso-
ciated stations’ storage medium and utilize the computational
resources  at  these  stations  for  local  computation  and  model
training to ensure privacy. The blockchain layer registers and
verifies  each  station,  asynchronously  transmitting  models  to
the DT layer via base stations (BS).
Blockchain Layer:This layer authenticates stations, tracks
local  models,  resists  poisoning  attacks,  and  incentivizes  par-
ticipation.   Managed   by   BS   with   computing   and   caching
resources, the blockchain maintains a distributed database for
synchronizing  data  and  storing  registration  information,  key
features,  and  FL  models.  Stations  in  the  same  learning  task
form  committees,  electing  leaders  via  consensus  algorithms.
The  leader  aggregates  local  models  into  a  global  model,
packing  hashes  into  a  new  block  for  verification.  Interaction
with the DT layer allows computation of station contributions,
influencing rewards and temporary model exclusions.
DT  Layer:This  layer  handles  computing  model  weights,
station  contributions,  updating  grid  replicas,  load  forecast-
ing,  fault  diagnosis,  and  decision  support.  By  integrating
sensors,  ML,  and  software  analytics,  the  DT  constructs  real-
time  models  for  smart  grid  simulation.  The  DT  continuously
evaluates contributions, updates the state based on the global
model,  and  controls  device  states.  Collaborating  with  device
and  blockchain  layers,  it  employs  artificial  intelligence  for
intelligent  decision-making,  distributed  resource  scheduling,
and advanced  analysis, enabling  instant  data processing,  grid
management, and bidirectional feedback.
B.  Digital Twin Model for Smart Grid
In  this  scheme,  the  power  generation  stations  on  the  gen-
eration  side,  transmission  stations  on  the  transmission  side,
substations,  distribution  stations,  and  users  on  the  consump-
tion  side  are  collectively  referred  to  as  station,  denoted  as:
Fig. 1.    The system architecture of PPSG. PPSG system is divided into three
layers: device layer, blockchain layer and digital twin layer.
## S={S
## 1
## ,S
## 2
## ,...,S
## H
}. Each station locally contains a series of
devices, such as voltage meters, electric field intensity sensors,
arc  sensors,  and  ultra-high  frequency  sensors,  denoted  as:
## M={M
## 1
## ,M
## 2
## ,...,M
## K
}. These devices establish connections
with  the  blockchain  and  DT  through  BS,  denoted  as:B=
## {B
## 1
## ,B
## 2
## ,...,B
p
}. By collecting data, the DT characterizes the
states  of  different  devices.  At  timet,  the  DT  of  stationS
h
## ,
denoted asDT
h
, can be expressed as:
## DT
h
## =
## 
## F
## [
ω
h
## (
τ
## )
## ]
## ,s
h
## (
t
## )
## ,s
h
## ,H
## ∗
h
## 
## (1)
whereω
h
(τ )represents  the  training  parameters  of  theh-th
station  in  roundτ,F[ω
h
(τ )]  represents  the  current  training
state  of  stationS
h
## ,s
h
(t)represents  the  current  system  state,
## s
h
represents  the  interaction  data  between  stationS
h
and
## DTDT
h
at the current time, andH
## ∗
h
represents the historical
interaction  data  between  station  and  DT,  such  as  historical
system  states,  historical  update  data,  and  historical  model
accuracies. Furthermore,s
h
(t)can be expressed as:
s
h
## (
t
## )
## =
## {
f
h
## (
t
## )
## ,E
h
## (
t
## )
## ,R
h
## (
t
## )
## }
## (2)
wheref
h
(t)represents the current computational capability of
the station, expressed as CPU idle rate,E
h
(t)represents energy
consumption, andR
h
(t)represents memory usage.
C.  Blockchain-Asynchronous Federated Learning Workflow
In PPSG, multiple stations collaborate on a shared ML goal,
such  as  intelligent  fault  diagnosis.  As  illustrated  in  Fig.2,
devices  (e.g.,  high-voltage  voltmeters,  ammeters,  cameras,
smart  meters)  at  different  stations  (labeled  A-F)  utilize  local
computational  resources  for  model  training.  Trained  models
are  then  forwarded  to  the  BS  and  stored  in  a  distributed
database.  The  caching  level  reflects  the proportion  of  cached
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4170IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
Fig.  2.The  workflow  of  PPSG.  The  process  and  relationship  of  local
model  uploading,  caching,  and  blockchain  packaging  under  asynchronous
aggregation are shown.
models relative to total stations; for instance, in a five-station
scenario,  a  60%  caching  level  retains  three  local  models  for
asynchronous aggregation. When sufficient models are cached,
the leader station aggregates and packages the hash values of
local and global models into a block for verification by other
stations.  Stations  consistently  use  the  latest  global  model  for
ongoing training.
Training  begins  with  the  establishment  of  an  initial  global
model  in  PPSG.  Upon  receipt,  stations  start  local  model
training.  For  example,  stations  A,  C,  and  F  first  complete
training,  producing  local  models  A0,  C0,  and  F0,  which  are
uploaded to the BS database for global model G0 aggregation.
A new Block 0 (global block) then stores the hash values of
A0, C0, F0, and G0. Subsequently, stations A, B, and E upload
A1, B0, and E0. Although A1’s upload fails due to a network
issue,  F1’s  successful  upload  without  waiting  for  C1  enables
global model G1’s computation from B0, E0, and F1, and the
creation of Block 1 for storage. Later, models A2 and outdated
C1   are   successfully   uploaded   for   integration   in   the   next
block.
## IV.  P
## ROBLEMANALYSIS ANDSOLUTION
This  section  examines  Non-IID  local  data  distribution  and
outdated  local  models  in  smart  grid  scenarios,  leading  to  an
AFL  scheme  with  dual  dynamic  aggregation  factor  in  PPSG
and a contribution-weighted stochastic election algorithm.
A.  Problem Formulation in Smart Grid
In  a  smart  grid,  the  complexity  and  heterogeneity  of  elec-
trical  devices,  along  with  the  dynamic  and  variable  power
grid  environment,  lead  to  Non-IID  conditions  even  among
devices  performing  the  same  task.  While  several  Non-IID
scenarios  are  outlined  in[6],  they  are  inadequate  for  the
complex and variable environment of smart grid. This system
designs  a  data  heterogeneity  measurement  scheme.  First,  the
stationS
h
collects  local  data  and  adds  random  perturbations
that  do  not  affect  the  data  distribution.  These  minimally
perturbed  data  are  periodically  sent  to  the  DT  and  stored  in
## H
## ∗
h
as  sample  data,SD
h
## ={x
## 1
## ,...,x
n
},  characterizing  the
station’s  data  distribution.  The  maximum  mean  discrepancy
algorithm (MMD)[38]is used to measure the data distribution
differences between different stations. The smaller the MMD
value  between  two  distributions,  the  more  similar  the  data
distributions are, which means less impact on model accuracy.
The  objective  of  AFL  is  to  train  a  global  model ̄ωfor
a  specific  task  using  numerous  devices  in  the  smart  grid.
MinimizingF( ̄ω)under  Non-IID  data  and  outdated  model
conditions is an optimization problem, i.e.,
̄ω=arg minF
## (
## ̄ω
## )
s.t.a. MMD
## 2
## 
## SD
h
## 1
## ,SD
h
## 2
## 
## ≥ξ
## 1
## ,∃h
## 1
## =h
## 2
## ,
or MMD
## 2
## 
## SD
h
## 3
## ,SD
h
## 
## ≥ξ
## 2
## ,∃h
## 3
or    b. ̄ω
## (
τ
## )
## ←ω
h
## (
λ
## )
,λτ,∃S
h
## ∈S,
h∈
## {
## 1,2,...,H
## }
## (3)
Constraint  a  represents  a  type  of  Non-IID  problem  in
distributed AFL scenarios, where two stationsh
## 1
andh
## 2
have
datasetsSD
h
## 1
andSD
h
## 2
with  an  MMD
## 2
value  exceeding  the
thresholdξ
## 1
or there exists a deviceh
## 3
whose datasetSD
h
## 3
has
an  MMD
## 2
value  exceeding  the  thresholdξ
## 2
compared  to  the
mean  of  the  sampled  datasetsSD
h
of  the  participants  in  the
learning task.ξis empirically determined for different learning
tasks. Constraint b represents the case in AFL, where, at the
τ-th aggregation round, deviceS
h
sends its local modelω
h
## (λ)
trained  based  on  theλ-th  round  global  model,  withλbeing
significantly  smaller  thanτ.  For  the  global  model ̄ω(τ ),the
modelω
h
(λ)is  too  outdated  and  affects  the  current  global
model’s accuracy.
## B.  Dual Dynamic Aggregation Factor
Authors  in[26],[37]have  demonstrated  that  the  weight
of  local  models  during  aggregation  significantly  affects  AFL
performance.   To   address   the   aforementioned   optimization
problem,  this  paper  designs  an  AFL  approach  with  dual
dynamic  aggregation  factor,  divided  into  a  data  similarity
measure factor based on improved MMD (i-MMD factor) and
model  timeliness  weight  factor  based  on  Newton’s  law  of
cooling (NCTW factor).
1)  The i-MMD Similarity Measurement Factor:Significant
differences   in   station   data   distribution   lower   local   model
accuracy,  which,  if  overly  relied  upon,  diminishes  global
model  accuracy.  The  i-MMD  factor  assigns  optimal  weights
to local models of stations with Non-IID data.
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4171
For  any  two  stations’  sample  data,SD
h
## 1
## ={a
## 1
## ,...,a
n
## 1
## }
andSD
h
## 2
## ={b
## 1
## ,...,b
n
## 2
},letP
h
## 1
andP
h
## 2
be the probability
distributions ofSD
h
## 1
andSD
h
## 2
, respectively. By mapping the
data  through  the  function(·)to  the  RKHSH,  the  i-MMD
betweenSD
h
## 1
andSD
h
## 2
is defined as:
## MMD
## 
## P
h
## 1
## ,P
h
## 2
## 
## =sup

## 

## H
## ≤1
## 
## E
a∼P
h
## 1
## [
## (a)
## ]
## −E
b∼P
h
## 2
## [
## (b)
## ]
## 
## (4)
whereE
a∼P
h
## 1
[·] andE
b∼P
h
## 2
[·] denote the expectations of the
distributionsP
h
## 1
andP
h
## 2
, respectively. The set of functions in
the unit ball of RKHSHis defined by
## 

## H
≤1. The biased
empirical  estimate  of  MMD  betweenSD
h
## 1
andSD
h
## 2
can  be
computed as:
## MMD
## 2
## 
## SD
h
## 1
## ,SD
h
## 2
## 
## =
## 
## 
## 
## 
## 
## 
## 1
n
## 1
n
## 1

i=1
## 
## (
a
i
## )
## −
## 1
n
## 2
n
## 2

j=1
## 
## 
b
j
## 
## 
## 
## 
## 
## 
## 
## 2
## H
## =
## 
## 
## 
## 
## 
## 
## 1
n
## 1
## 2
n
## 1

i=1
n
## 1

i

## =1
k
## 
a
i
## ,a
i

## 
## −
## 2
n
## 1
n
## 2
n
## 1

i=1
n
## 2

j=1
k
## 
a
i
## ,b
j
## 
## +
## 1
n
## 2
## 2
n
## 2

j=1
n
## 2

j

## =1
k
## 
b
j
## ,b
j

## 
## 
## 
## 
## 
## 
## 
## =tr
## (
## KL
## )
## (5)
where:
## K=


## K
s,s
## K
s,t
## K
t,s
## K
t,t

## (6)
and
## L
ij
## =
## ⎧
## ⎪
## ⎪
## ⎨
## ⎪
## ⎪
## ⎩
## 1
n
## 2
## 1
## ,a
i
## ∈SD
h
## 1
## 1
n
## 2
## 2
## ,b
j
## ∈SD
h
## 2
## −
## 2
n
## 1
n
## 2
## ,otherwise
## (7)
where,(·)represents  the  kernel-induced  feature  mapping,
and(a)=k(a,·). Note thatk(a,b)=(a), (b). PPSG
employs  a  Gaussian  kernel  functionk(a,b)to  calculate  the
i-MMD factor, defined as:
k(a,b)=exp
## 
## −
a−b

## 2
## 2σ
## 2
## 
## (8)
whereσis the width of the Gaussian kernel.
The i-MMD factorδ
k
for stationkis calculated as:
δ
k
## =exp
## 
## −℘MMD
## 
## P
k
## ,P
target
## 
## (9)
where℘is  an  adjustable  hyperparameter,  andP
target
is  the
data distribution of the task-initiating station.
2)  The  Model  Timeliness  Weighting  Factor  NCTW:The
timeliness weight factor, grounded in Newton’s law of cooling,
adjusts  the  old  model’s  weight  during  global  model  aggre-
gation.  According  to  this  principle[39],  an  object’s  cooling
rate  is  proportional  to  the  temperature  difference  with  its
environment, leading to heat transfer and gradual cooling:
## T

## (
t
## )
## =
dT
dt
## =−∂
## (
## T
## (
t
## )
## −H
## 0
## )
## (10)
Algorithm  1Dual Dynamic Aggregation Factor
1:functionCLIENTUPDATEOn stations
2:foreach local epoch inEdo
3:download newest global model ̄ω
## (
λ
## )
from the BS
## 4:ω
h
## (
λ
## )
←LocalTrain( ̄ω
## (
λ
## )
, localTrainData)
## 5:uploadω
h
## (
λ
## )
to the BS
6:end for
7:end function
## 8:
## 9:
functionAGGREGATIONOn the aggregator of DT
10:Wa i tω
h
## ,h∈
## {
## 1,2, ...,H
## }
in the distributed database
## 11:foreachω
h
## ,h∈
## {
## 1,2, ...,H
## }
do
## 12:δ
h
## ←exp
## 
## −℘MMD(P
h
## ,P
target
## )
## 
## 13:
τ
h
## ←W
## 0
## +
## (
## MW
## 0
## −W
## 0
## )
e
## −∂
## 
τ−λ
λ
## 
14:end for
## 15: ̄ω
## (
τ
## )
## =
## 
## ̄ω
## (
τ−1
## )
## +
## 
## H
h=1

τ
h
δ
h
ω
h
## 
## /
## 
## 1+
## 
## H
h=1

τ
h
δ
h
## 
## 16:upload Hash( ̄ω
## (
τ
## )
),allHash(ω
h
)to the blockchain
## 17:save ̄ω
## (
τ
## )
to the distributed database
18:end function
whereT

(t)denotes  the  derivative  of  temperatureTwith
respect to timet(i.e., cooling rate). The constant∂represents
the  ratio  between  the  ambient  temperature  and  the  cooling
rate. Different materials have different values of∂, whileH
## 0
represents the indoor temperature.
Limited  computing  resources  at  some  stations  delay  local
model   training,   degrading   global   model   accuracy   due   to
outdated models. Newton’s law of cooling adjusts weights in
global  aggregation[23].  The  NCTW  factor  for  stationS
h
at
roundτis computed as:

τ
h
## =W
## 0
## +
## (
## MW
## 0
## −W
## 0
## )
e
## −∂
## 
τ−λ
λ
## 
## (11)
where,τrepresents  the  current  round  number,λenotes  the
round of the global model on which the local model submitted
by the stationS
h
is based,W
## 0
signifies the weight value of the
oldest model,MW
## 0
represents the weight value of the freshest
model, and∂is the decay coefficient depending on the training
task.  The  larger∂,  the  greater  the  decay  coefficient,  and  the
smaller the proportion of outdated models in the global model.
The  weight  of  local  models  decays  based  on  freshness;
newer  models  have  greater  weight,  older  models  less,  decay
rate  governed  by  the  decay  coefficient.  The  global  model  at
roundτis computed as follows:
## ̄ω
## (
τ
## )
## =
## ̄ω
## (
τ−1
## )
## +
## 
## H
h=1

τ
h
δ
h
ω
h
## 1+
## 
## H
h=1

τ
h
δ
h
## (12)
3)  Algorithm   for   Dual   Dynamic   Aggregation   Factor:
Algorithm1outlines  the  implementation  of  dual  dynamic
aggregation factor in PPSG. PPSG comprises two main func-
tions: Client Update (lines 1-7) and Aggregation (lines 9-18).
Prior to training a new local model ̄ω(λ), station downloads the
latest  global  model ̄ω(λ)from  the  BS’s  distributed  database,
as specified in lines 3 and 4. Post-training, the updated local
model ̄ω(λ)is  uploaded  to  the  BS’s  database  (line  5).  If  the
local epochEis not yet complete, the loop continues, as shown
in line 2.
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4172IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
From  the  perspective  of  the  committee  leader,  the  aggre-
gation  process  begins  when  the  distributed  database  receives
the  local  modelsω
h
,h∈{1,2,...,H}that  H  meets  the
required cache level, as shown in line 10. For each local model
ω
h
,  the  dual  dynamic  factor  calculator  of  DT  calculates  the
i-MMD factorδ
h
according  to  Eq.(9)and  the  NCTW  factor

τ
h
according to Eq.(11), as described in lines 12 and 13. All
received  local  models  are  processed  iteratively,  as  shown  in
line 11. Subsequently, a new global model ̄ω(τ)is computed
using Eq.(12), as illustrated in line 15. Ultimately, the leader
station  uploads  the  hash  of  the  global  model  and  all  local
model  hashes  to  the  blockchain,  while  preserving  the  global
model ̄ω(τ )in  the  distributed  database,  as  indicated  in  lines
16 and 17.
4)  Intuitive  Explanation  for  Dual  Dynamic  Aggregation
Factor:To  enhance  readability,  we  provide  here  a  concise
example  to  illustrate  the  derivation  and  practical  intuition
behind our dual dynamic aggregation factor. Specifically, our
method consists of the i-MMD factor to handle Non-IID data
and the NCTW factor to address outdated local models:
•i-MMD  Factor:We  quantify  the  data  distribution  gap
between   a   local   station   and   a   target   distribution   by
employing  a  MMD  metric.  When  the  MMD  value  is
large, indicating a significant discrepancy, the exponential
term  in  our  factor  (i.e.,e
## −℘·MMD
)is  small,  thereby
causing  local  models  to be  given  smaller  weights  in the
aggregation, further improving convergence performance
in Non-IID scenarios.
•NCTW  Factor:Inspired  by  Newton’s  Law  of  Cooling,
this  factor  reduces  the  contribution  of  stale  (lagging)
local  models.  Concretely,  if  a  station’s  model  is  based
on a much older global model (i.e., the station is several
rounds behind), the factor decays exponentially and thus
lowers that station’s influence in the aggregation step.
Illustrative  Example:Suppose  we  are  at  global  roundτ,
and  a  certain  stationS
h
submits  a  local  model  based  on  the
global model from roundλ.LetW
## 0
## =0.1,MW
## 0
=1.0, and a
decay coefficient∂=0.5. If the station is 5 rounds late (i.e.,
τ−λ=5,  withλ=10),  then  its  NCTW  factor
τ
h
can  be
calculated from:

τ
h
## =W
## 0
## +
## (
## MW
## 0
## −W
## 0
## )
e
## −∂
## 
τ−λ
λ
## 
## ≈0.1+0.9·e
## (
## −0.5×0.5
## )
## ≈0.8
Hence,  although  the  local  model  is  somewhat  outdated,
it  still  retains  about  80%  of  its  potential  contribution.  As
the  model  becomes  increasingly  stale,  the  exponential  term
quickly  diminishes,  preventing  excessively  outdated  updates
from degrading the global model.
Novelty:For asynchronous federated learning within smart
grid,  we  introduce  the  i-MMD  and  NCTW  factors,  which
explicitly account for the divergence in grid data distributions
(i-MMD) and the temporal relevance of models (NCTW). This
dual  dynamic  aggregation  factor  facilitates  the  simultaneous
resolution  of  these  two  primary  challenges  within  a  unified
framework,  a  capability  that  has  been  largely  unaddressed  in
existing research.
C.  The Contribution-Based Weighting Stochastic Election
## Algorithm
In  AFL  for  smart  grid,  measuring  station  contributions  is
vital  for  resisting  attacks  and  enhancing  learning  accuracy.
Stations  with  higher  contributions  should  be  more  likely  to
be  elected  as  leaders  in  the  computing  system.  Our  algo-
rithm,   unlike   traditional   ones   focused   solely   on   security,
also  accounts  for  DT  status,  learning  quality,  and  malicious
interactions.
1)  Contribution Measurement:Based on a subjective logic
model, the contribution of stationS
h
to BSpat timetduring
interaction can be represented as:
## C
t
## S
h
## →p
## =
f
h
## (
t
## )
u
t
h→p
## ·q
t
h→p
## ·
## 
α
t
h
α
t
h
## +β
t
h
## 
## (13)
wheref
h
(t)denotes  the  computing  capability  of  stationS
h
at  timet,u
t
h→p
represents  the  probability  of  data  packet
transmission failure,α
t
h
denotes the number of positive inter-
actions,β
t
h
represents  the  number  of  malicious  behaviors
such  as  uploading  low-quality  local  models,  andq
t
h→p
## =
## MMD
## 2
## (ω
h
, ̄ω),  indicating  the  deviation  between  the  local
model held by stationS
h
and the global model (setq
t
h→p
to 1
during  the  initial  election).  The  contribution  value  of  station
## S
h
to the system can be calculated as:
## C
h
## =
## T

t=1
b
t
h→p
## +κu
t
h→p
## (14)
where,κ∈[0,1]  represents  the  coefficient  affecting  the
contribution value’s uncertainty.
2)  The Weighting Stochastic Election Algorithm:In PPSG,
after  generating  several  new  blocks,  a  new  committee  chair-
person  is  elected.  stations  with  higher  contributions  to  the
system  are  more  likely  to  be  elected  as  leader  station.  As
depicted in Fig.3, the genesis block Block0 is initially created
by  a  randomly  chosen  hydropower  station.  The  blockchain’s
consensus algorithm guarantees that all replica blocks on BS
match the original Block0. Next, the contribution of all stations
in  the  committee  are  calculated  and  mapped  to(0,1].  For
eachS
h
∈Sin  the  training  task,C

h
## =
## C
h
## 
## H
h=1
## C
h
,  and  random
numbersr
h
=random(0,1)are  generated  according  to  the
weighted random sampling (WRS) algorithm[40], calculating
p
h
## =r
## 1/C

h
h
. The nuclear power station with the highestpvalue
becomes  the  leader  station.  The  rate  of  electing  a  committee
chairperson  is  the  inverse  of  the  number  of  blocks  mined
before a new chairperson is chosen. If the election rate is 1/20,
a  new  chairperson  is  determined  after  every  20  blocks  are
added  to  the  blockchain.  Following  the  identical  calculation
method,  the  office  station  and  the  thermal  power  station  will
be elected as the third and fourth leader station respectively.
Stations   with   significant   contributions   receive   rewards,
while low-contribution stations may be excluded from aggre-
gation  and  reevaluated  by  the  leader  station  until  meeting
the  contribution  threshold  for  training.  Continuous  DT-based
evaluation, factoring in computing capability and transmission
stability,  effectively  assesses  station  contributions,  mitigates
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4173
Fig. 3.The election of the committee chairperson is based on the contribution. The correlation between the blockchain’s hash value and the model in the
distributed database is illustrated.
security threats from malicious participants, enhances system
robustness, and reduces cheating risks.
Novelty:A “Proof  of Contribution”  consensus  mechanism
is  designed  to  address  the  characteristics  of  dt  technology
and the smart grid environment. Unlike existing methods that
select  based  solely  on  the  accuracy  of  local  models,  our
approach  comprehensively  takes  into  account  factors  such
as   the   computational   capabilities   of   devices,   transmission
success  rates,  and  their  historical  behaviors  (including  both
positive  and  malicious  actions).  This  mechanism  not  only
possesses resilience against poisoning attacks but also balances
election  efficiency  and  system  security  through  contribution
measurement and random sampling.
D.  Cross-Layer Workflow and Interaction in PPSG
To ensure that the DT accurately reflects the real-time state
of  physical  systems,  PPSG  initially  employs  a  small  set  of
non-sensitive data (see the related discussion in SectionIV)to
build a virtual models of physical smart grid systems. Multiple
tasks  are  then  launched  to  perform  asynchronous  federated
learning. Under strict privacy constraints, each station’s local
data is trained and aggregated so that the DT can progressively
evolve to predict the state of physical entities. Building upon
the PPSG architecture outlined earlier, as well as the proposed
asynchronous federated learning process, dual dynamic factor
mechanism, and contribution-based consensus algorithm, this
subsection  describes  how  the  device  layer,  the  blockchain
layer, and the DT layer engage in real-time interaction.
*Task   initiation:When   the   DT   layer   requires   new
prediction  or  control  tasks  for  the  power  grid,  it  publishes  a
training task, corresponding to the “
★Tasks” in Fig.4.
Step  1  –  Local  training:Upon  receiving  the  new  task,
each  station  performs  several  rounds  of  localized  training,
denoted  by
①in  Fig.4.  Because  station  data  are  typically
sensitive, model training remains within each station, thereby
mitigating privacy risks that might arise from centralized data
collection.
Step  2  –  Model  upload  and  caching:After  one  or  more
rounds of local training, each station uploads its model to the
BS within the blockchain layer, where the model is temporarily
cached, as indicated by
## ②in Fig.4.
Step  3  –  Aggregation  and  global  model  update:Once
the  BS  has  cached  a  sufficient  number  of  local  models  or
a  specified  trigger  condition  is  met,  the  DT  layer  retrieves
these  models,  invokes  its  aggregator,  and  applies  the  dual
dynamic  factor  mechanism  (i.e.,  the  i-MMD  and  NTCW
factors described in SectionIV-B) to combine asynchronously
arriving  local  models.  The  newly  generated  global  model  is
then returned to the BS, shown as
## ③in Fig.4.
Election  (Parallel  Process):Concurrently,  at  fixed  time
intervals or after a set number of blocks has been produced, the
blockchain layer periodically conducts leader station election
based  on  DT’s  contribution  evaluations  (see  SectionIV-C).
This process can proceed in parallel with the overall training
task.
Step  4  –  Block  packaging:After  the  BS  receives  the
updated  global  model,  the  leader  station  packages  the  latest
global model hash together with the corresponding local model
hashes into a new block, then submits it for consensus among
other  stations.  Once  verification  is  complete,  the  block  is
formally added to the blockchain (
## ④in Fig.4).
Step  5  –  Distributing  the  global  model  &  continuing
training   (parallel   to   step   4):In   tandem   with   the   block-
packaging  operation,  the  BS  distributes  the  newly  updated
global  model  to  all  stations,  as  depicted  by
## ⑤in  Fig.4.
Stations  then  begin  the  next  local  training  round,  effectively
repeating the procedure labeled
## ①.
*Iteration  of  steps  1–5:Local  training,  global  model
aggregation, on-chain confirmations, and leader election inter-
leave  in  multiple  asynchronous  rounds,  continuing  until  the
DT  layer  determines  that  the  global  model  has  converged  or
the learning task has concluded.
Step  6  –  DT  feedback  and  extended  control:Upon  task
completion,  the  DT  layer  conducts  in-depth  simulations  and
evaluations  of  the  power  grid  based  on  the  converged  global
model  and  multi-source  measured  data.  If  an  anomaly  or
dispatch   requirement   arises,   the   DT   layer   issues   control
instructions  to  the  device  layer  to  orchestrate  physical-side
adjustments.  For  more  complex  decisions,  human  experts  or
additional external inputs can be incorporated to further refine
the outcome (
## ⑥in Fig.4).
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4174IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
Fig. 4.Detailed Cross-Layer Workflow and Interaction in PPSG. Through cross-layer interaction, PPSG combines local training in the device layer, model
management and leader election in the blockchain layer, and dual dynamic factor aggregation in the digital twin layer through asynchronous federated learning.
Through the aforementioned cross-layer interactions, PPSG
seamlessly combines local training in the device layer, model
management   and   leader   election   in   the   blockchain   layer,
and  dual  dynamic  factor  aggregation  in  the  DT  layer  via
asynchronous  federated  learning.  This  design  simultaneously
protects data and model privacy while improving accuracy and
responsiveness  under  Non-IID  conditions.  Ultimately,  PPSG
provides  a  flexible,  efficient,  and  trustworthy  solution  for
distributed prediction, diagnosis, and control services in smart
grid.
## V.   E
## VA L U AT I O N
This  section  presents  experiments  evaluating  the  proposed
PPSG  scheme  in  terms  of  learning  performance,  efficiency,
reliability, and its performance on real datasets. The following
research questions are addressed:
•RQ1:How effective is the independent aggregation factor
in PPSG compared to existing similar schemes?
•RQ2:How does PPSG improve learning performance and
efficiency over the current state-of-the-art?
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4175
•RQ3:Is  PPSG  reliable  enough  to  withstand  poisoning
attacks?
•RQ4:How does PPSG perform on real-world datasets in
a smart grid environment?
•RQ5:How  scalable  is  the  PPSG?  How  does  PPSG
perform with hundreds or thousands of nodes?
## A.  Experimental Setup
1)  Cluster  Configuration:A  Kubernetes  cluster  of  GPU
and   CPU   nodes   emulates   smart   grid   stations   for   local
training.  GPU  nodes  use  Nvidia  GeForce  GTX  1080,  6-core
Intel  i5-11400,  and  16GB  DDR4,  while  CPU  nodes  have
6-core  Intel  i5-11500  and  16GB  DDR4.  Raspberry  Pi  B4
devices  with  4-core  CPUs  and  8GB  RAM  model  BSs  with
distributed  databases.  The  DT  server  operates  on  a  system
with  NVIDIA  GeForce  RTX  3090,  AMD  Ryzen  7  5700X,
and 64GB DDR4. All nodes run 64-bit Ubuntu 18.04 OS. ML
models are trained using PyTorch v1.9.1 on Python 3.8, with
GPUs leveraging CUDA 10.2 and cuDNN v7.2.1. Blockchain
smartcontracts,developedusingHyperledgerFabric
v2.3.3,   coordinate   model   training,   aggregation,   and   block
packaging.
In  order  to  answer  the  RQ1-RQ4,  containers  representing
stations  are  allocated  specific  hardware  resources,  creating
a   heterogeneous   training   environment.   Twenty   containers,
including 10 GPU and 10 CPU, simulate smart grid stations.
CPU containers vary in allocation, with 6, 3, or 1 CPU cores.
GPU  containers  act  as  fast  workers,  while  CPU  containers
serve as standard clients or stragglers. To further address RQ5,
we deployed an additional 1,000 lightweight virtual containers
in the Kubernetes cluster to rigorously evaluate the scalability
of PPSG under more extensive conditions.
The  blockchain,  maintained  by  Raspberry  Pi  devices  and
driven by smart contracts, allows the leader station to manage
model hash values. Per Hyperledger Fabric[41]parameters, a
new block is generated when either the waiting time reaches
20  seconds  or  the  cache  level  hits  the  model  limit.  Upon
creation  of  a  new  global  model,  the  smart  contract  directs
stations  that  completed  the  previous  round  to  download  the
updated model from the BS database for subsequent training.
The DT server oversees the entire process and updating models
in real-time.
2)  Datasets,  Models,  and  Comparison  Schemes:The  ML
models are trained on three benchmark datasets: MNIST[5],
FMNIST[37],EMNIST[20],  and  one  real-world  dataset:
UK  power  Network  smart  meter  energy  consumption  dataset
(UK-SMEC)[42].  UK-SMEC,  collected  by  the  UK’s  largest
distribution   company   UK   Power   Network,   contains   half-
hourly  energy  consumption  data  from  5,567  households  in
London  from  2011  to  2014.  The  ML  models  used  include
Convolutional Neural Networks (CNN) and Long Short-Term
Memory (LSTM) networks.
According  to[19],[20],  some  clients  hold  a  few  classes
of   data   with   different   sizes   to   set   the   Non-IID   configu-
ration   for   MNIST   and   FMNIST   datasets.   EMNIST   data
Non-IID  nature  is  due  to  differences  in  handwriting  styles
between  authors.  The  Non-IID  characteristic  of  UK-SMEC
data  stems  from  varying  power  consumption  patterns  among
users. Consistent with[5],[20],[26], in CNN experiments on
MNIST, FMNIST, and EMNIST, the learning rate isη=0.01,
with the number of local training epochs set toE=2, and a
local minibatch size oflb=64. For the LSTM model on the
UK-SMEC dataset, these parameters are the same except the
local minibatch size islb=16.
To  evaluate  PPSG,  the  comparison  includes  several  state-
of-the-art schemes:
1)FedProx:A    synchronous    FL    scheme    addressing
Non-IID data issues through regularization terms[19].
2)FedAdam:A  synchronous  FL  scheme  using  adaptive
learning rates to tackle Non-IID data[20].
3)FedAsync:A traditional asynchronous FL scheme[26].
4)KAFL:An   asynchronous   FL   scheme   dynamically
adjusting aggregation weights for heterogeneous training
environments[27].
5)DBAFL:An  asynchronous  FL  scheme  with  dynamic
scaling factors integrated with blockchain[37].
6)FedAvg:A traditional synchronous FL scheme[5].
7)Centralized:Training the ML model by centralizing all
data to a single node.
B.  Analysis of Experimental Rationality
1)  Choice and Rationale of the Benchmark:Dataset ratio-
nale:In  this  work,  we  evaluate  our  proposed  method  on
multiple  publicly  available,  widely  used  standard  datasets
(MNIST, FMNIST, EMNIST) and a real-world power-system
dataset (UK-SMEC). These datasets are universally acknowl-
edged by the community and offer unique advantages:
-  MNIST, FMNIST, and EMNIST are classic image-based
datasets commonly used for federated learning evaluation,
especially under Non-IID scenarios. They effectively test
performance under different data distributions and model
complexities.
-  UK-SMEC is a real-world smart-grid energy consumption
dataset that reflects actual electricity usage patterns. Since
these  patterns  are  typically  highly  heterogeneous  and
time-varying,  this  dataset  serves  as  an  excellent  test  for
assessing the model’s performance in complex, real-world
settings.
Experiment  environment  design:Experiments  were con-
ducted  on  a  mixed  cluster  containing  both  GPU  nodes  and
CPU nodes to simulate the diversity of computing devices in
a real smart grid. To ensure reproducibility and objectivity, we
followed these principles for all methods:
-  Same or similar initial model architectures: All compared
methods  use  the  same  type  of  CNN  or  LSTM  model
(depending  on  whether  the  task  is  image-based  or  time-
series), differing solely in their training algorithms.
-  Consistent  hyperparameter  settings:  Whenever  possible,
learning  rates,  batch  sizes,  number  of  training  epochs,
and  other  parameters  are  held  constant  across  different
comparison methods.
-  Uniform data preprocessing and partitioning: For MNIST,
FMNIST,  and  EMNIST,  data  partitioning  is  carried  out
with an identical strategy to simulate Non-IID conditions
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4176IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
Fig. 5.    Comparing the average test accuracy of the global model using the proposed i-MMD factor and five similar schemes under Non-IID data conditions.
across   stations.   For   UK-SMEC,   we   adopt   the   same
preprocessing pipeline for all methods.
-  Similar   or   equivalent   network   latency/communication
costs: Whether in asynchronous or synchronous settings,
we apply identical or similar network delay models to all
methods  in  order  to  replicate  real-world  communication
constraints.
2)  Fairness   of   the   Comparison   Schemes:We   compare
our  proposed  PPSG  against  several  representative  federated
learning  and  blockchain-enhanced  methods  under  the  same
environment  to  demonstrate  performance  in  heterogeneous
environments and under non-IID conditions:
•FedAvg[5]/ FedProx[19]/ FedAdam[20]: Three classic
or   improved   synchronous   federated   learning   schemes
widely used in the literature.
•FedAsync[26]/ FedProx+Async / KAFL[27]/DBAFL
[37]:  Representative  asynchronous  federated  learning  or
blockchain-based approaches.
•Centralized: A baseline that aggregates all data on a single
node for training, serving as the idealized upper bound.
•PPSG   (our   proposed   scheme):   Integrates   blockchain,
digital  twin,  and  our  dual  dynamic  factor  approach  for
asynchronous  federated  learning,  validated  on  different
performance indices and stability metrics.
In the experimental comparisons, we ensure:
•All baseline algorithms are replicated using their original
or official hyperparameter settings.
•The  same  hardware  environment,  data  partitioning  tech-
niques, and hyperparameter tuning ranges are applied to
all schemes.
•Results  are  averaged  over  multiple  runs  to  reduce  the
influence of randomness.
## 3)  Main Evaluation Metrics:
-  Model accuracy: For image classification tasks (MNIST,
## FMNIST, EMNIST).
-  RMSEandMAE:Forpowerloadforecasting
## (UK-SMEC).
-  Convergence rounds and total training time: To measure
efficiency  and  speed  in  asynchronous  settings  with  het-
erogeneous resources.
-  Robustness   under   poisoning   attacks:   Additional   tests
where some clients intermittently upload invalid models.
Based  on  these  benchmarks  and  the  rigorous  experimen-
tal  pipeline,  our  comparison  experiments  can  convincingly
demonstrate the strengths and weaknesses of each method.
C.  Key Experimental Results and Comparative Analysis
1)  Effectiveness  of  Independent  Aggregation  Factors:To
address  RQ1,  ablation  experiments  are  conducted  to  apply
each  aggregation  factor  individually  across  multiple  datasets
and   compare   them   with   advanced   schemes   of   similar
functionality.
The  i-MMD  Factor  Analysis:  The  i-MMD  factor  is  tested
using  three  datasets  (MNIST,  FMNIST,  and  EMNIST)  with
Non-IID  settings,  and  compared  against  FedAvg,  FedProx,
FedAdam,  FedAvg-IID  (FedAvg  with  IID  data  distribution),
and  Centralized  (training  with  all  data  on  a  single  node).
Experiments  are  conducted  on  10  GPU-equipped  stations,
ensuring  equal  data  volume  per  station,  with  200  training
rounds.   As   illustrated   in   Fig.5,   the   Centralized   scheme
exhibits the fastest convergence and highest accuracy across all
datasets. The i-MMD scheme shows comparable convergence
on   Non-IID   data   to   FedAvg   on   IID   data.   Compared   to
FedProx,  FedAdam,  and  FedAvg,  i-MMD  scheme  achieves
faster  convergence  and  higher  global  accuracy.  Overall,  the
i-MMD factor shows significant advantages in handling Non-
IID  data,  combining  high  convergence  speed  with  accurate
predictions.
The NCTW Factor Analysis: The NCTW factor is evaluated
using IID settings of MNIST, FMNIST, and EMNIST datasets,
simulating  scenarios  with  straggler  workers.  The  compari-
son  schemes  include  FedAsync,  KAFL,  and  FedProx  with
asynchronous mechanisms (FedProx-Async). Experiments are
conducted  on  10  GPU  stations  and  10  CPU  stations  with
varying  core  counts  (6,  3,  1),  with  2000  training  rounds.
As   depicted   in   Fig.6,   the   NCTW   factor   outperforms   in
both convergence speed and global model accuracy across all
datasets. FedAsync exhibits the slowest convergence and low-
est accuracy. KAFL generally exceeds FedProx-Async, except
on  MNIST  where  KAFL’s  convergence  lags.  These  results
confirm  NCTW’s  significant  improvements  in  convergence
speed   and   accuracy   in   straggler   scenarios,   outperforming
current AFL schemes.
The Decay Coefficient(∂)Analysis:∂is a critical parameter
in  controlling  the  decay  speed  of  the  NCTW  factor,  directly
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4177
Fig. 6.Comparing the average test accuracy of the global model using the proposed NCTW factor and three similar schemes in straggler scenarios.
Fig.  7.Comparing  the  variation  in  average  classification  accuracy  and
convergence  rounds  across  MNIST,  EMNIST,  and  FMNIST  datasets  as  the
NCTW decay coefficient(∂)changes.
influencing the rate of model weight updates. A larger decay
coefficient corresponds to faster decay, while a smaller value
results  in  slower  decay.  In  our  experiments,  the  weight  of
the  freshest  model(MW
## 0
)was  set  to  1,  while  the  weight  of
the oldest model(W
## 0
)was set to 0.1, to study the impact of
different decay coefficients on model performance. As shown
in (a) of Fig.7, average accuracy across MNIST, FMNIST, and
EMNIST datasets follows a noticeable trend: it first rises and
then declines with increasing∂, peaking at∂≈0.5 (approx-
imately 99% for MNIST, 91.5% for FMNIST, and 93.2% for
EMNIST). This finding suggests that moderate decay enhances
model  stability  and  accuracy.  Similarly,  convergence  rounds,
shown  in  (b)  of  Fig.7,  exhibit  a  U-shaped  trend,  with  the
optimal  point  also  occurring  at∂≈0.5  (approximately  300
rounds for MNIST, 1050 rounds for FMNIST, and 550 rounds
for  EMNIST).  In  summary,  a  moderate  decay  coefficient
(∂≈0.5)balances  accuracy  and  convergence  efficiency,
highlighting its importance in asynchronous federated learning
and its potential for improving federated system performance.
Result  1:  The  i-MMD  and  NCTW  factors  in  PPSG
demonstrate  significant  advantages  in  handling  Non-IID
data  distribution  and  scenarios  with  straggler  workers,
respectively.
2)  Performance   and   Efficiency   Analysis   of   PPSG:To
address  RQ2,  the  PPSG  scheme  is  compared  with  state-of-
the-art  schemes,  including  FedAsync,  KAFL,  DBAFL  (with
blockchain),  and  FedProx+Async,  using  Non-IID  settings  of
MNIST,  Fashion-MNIST,  and  EMNIST  datasets.  The  exper-
iments  employ  10  GPU  stations  and  10  CPU  stations  with
varied core counts (6, 3, 1), incorporating model upload delays
to simulate real network conditions, with 2000 training rounds.
AsshowninFig.8, PPSG outperforms all datasets, achiev-
ing   the   fastest   convergence   and   highest   accuracy.   PPSG
converges  in  250  rounds  on  MNIST,  exceeding  98.5%  accu-
racy,  and  within  500  and  200  rounds  on  Fashion-MNIST
and  EMNIST,  respectively.  KAFL  converges  quickly  with
slight   fluctuation   since   it   only   accepts   only   fast   models,
but  its  accuracy  is  lower  than  PPSG.  DBAFL,  FedAsync,
and  FedProx+Async  show  slower,  less  accurate  convergence
with   larger   fluctuations.   DBAFL’s   dynamic   scaling   factor
improves convergence speed and accuracy over FedAsync and
FedProx+Async but still lags behind PPSG. Traditional algo-
rithms like FedProx struggle with stragglers and Non-IID data,
even asynchronously. These results confirm PPSG’s superiority
in  handling  data  and  device  heterogeneity,  achieving  high
accuracy in fewer rounds with stable performance.
To  evaluate  PPSG’s  time  efficiency,  the  total  convergence
time  for  each  scheme  on  different  datasets  was  recorded.
As  shown  in  Fig.10,  FedProx+Async  and  FedAsync  require
over   40   minutes   to   converge.   DBAFL’s   dynamic   scaling
improves convergence speed, reducing time to around 40 min-
utes  despite  blockchain  overheads.  KAFL  converges  faster
than  PPSG  on  some  datasets  by  discarding  slower  models
and  excludes  blockchain  operations.  However,  PPSG,  with
its  i-MMD  and  NCTW  factors,  achieves  rapid  convergence,
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4178IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
Fig. 8.    Comparing the average test accuracy of the global model of the proposed scheme and four mainstream schemes under conditions with both Non-IID
data distribution and straggler workers.
Fig. 9.Comparing the average test accuracy of PPSG scheme with DBAFL and FedAsync scheme under different levels of poisoning attacks.
Fig.  10.Comparing  the  average  time  cost  to  train  CNN  models  to
convergence  on  the  MNIST,  FMNIST,  and  EMNIST  datasets  across  five
different schemes.
minimizing training rounds. Even with blockchain packaging,
PPSG outperforms blockchain-based schemes in overall speed
due to its synchronized local training and packaging.
Result  2:  Compared  to  existing  advanced  schemes,
PPSG offers optimal model accuracy and high efficiency
on Non-IID datasets and heterogeneous devices.
3)  Robustness   Against   Attacks:To   address   RQ3,   vary-
ing  proportions  (10%,  30%,  50%)  of  stations  are  randomly
designated  as  malicious  to  simulate  poisoning  attacks.  These
stations  intermittently  upload  either  valid  or  fake  models.
We  selected  PPSG,  DBAFL,  and  FedAsync  as  comparison
methods,  as  these  approaches  represent  the  mainstream  and
advanced   solutions   in   the   current   field   of   asynchronous
federated  learning.  Notably,  FedAsync  lacks  defense  mecha-
nisms, while DBAFL’s defense mechanism relies on dynamic
weighting based on local model accuracy. These factors allow
us  to  effectively  evaluate  PPSG’s  low-contribution  blocking
mechanism.
As  shown  in  Fig.9,  FedAsync  fails  to  maintain  model
integrity  when  subjected  to  such  attacks  due  to  its  lack  of
mechanisms for detecting or mitigating malicious updates. In
contrast,  DBAFL  demonstrates  a  higher  level  of  resilience
by  effectively  resisting  up  to  20%  malicious  stations.  This
robustness  is  achieved  through  DBAFL’s  dynamic  weighting
defense  mechanism,  which  adjusts  the  influence  of  individ-
ual  model  updates  based  on  their  local  accuracy.  However,
when  the  proportion  of  malicious  stations  increases  to  50%,
DBAFL’s  effectiveness  diminishes  significantly,  resulting  in
a   reduction   of   global   accuracy   to   80%   and   causing   the
training process to fail to converge. This decline is primarily
due  to  DBAFL  inadvertently  lowering  the  weights  of  valid
model  updates  while  attempting  to  mitigate  the  impact  of
malicious  ones,  thereby  impairing  the  overall  convergence
of   the   global   model.   In   stark   contrast,   PPSG   maintains
reasonable  accuracy  with  only  a  5%  decline,  even  in  the
presence of 50% malicious stations. This superior performance
is  attributed  to  PPSG’s  ability  to  intelligently  reject  low-
contribution models without permanently excluding valid ones.
This   approach   allows   PPSG   to   effectively   neutralize   the
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4179
## TA B L E  I
## C
## OMPARISON OFRMSEANDMAE BETWEENPPSGANDFEDASYNC
## SCHEMES INMONTHLYLOADPREDICTION
influence  of  malicious  updates  while  preserving  the  integrity
and diversity of legitimate contributions. Consequently, PPSG
not only sustains high global accuracy despite severe poisoning
but  also  ensures  the  convergence  of  the  training  process
by  maintaining  a  balanced  and  robust  aggregation  of  model
updates.
Result   3:   PPSG   exhibits   remarkable   reliability   in
defending  against  poisoning attacks, effectively identify-
ing and mitigating covert poisoning attacks.
4)  Performance on Real-World Datasets:To address RQ4,
the  UK-SMEC  real-world  power  grid  dataset  was  utilized  to
simulate  the  power  grid  environment.  Data  from  21  users
were  extracted  from  a  total  of  5,567,  with  data  from  one
user designated for global model testing and the remaining 20
users’ data employed as local data for 20 individual stations.
The  FedAsync  was selected  as a benchmark  comparison  due
to  its  representative  role  in  industrial  applications  and  its
ability  to  reflect  the  performance  of  traditional  methods  in
handling complex real-world data. The performance of smart
grid energy consumption prediction tasks was evaluated using
Root  Mean  Square  Error  (RMSE)  and  Mean  Absolute  Error
(MAE) metrics.
Overall, the PPSG scheme outperforms the AFL scheme in
the energy consumption prediction task. As shown in TableI,
in  the  monthly  load  prediction  comparison  experiment,  the
PPSG  scheme  achieves  an  average  RMSE  of  0.1714,  while
the   AFL   scheme   has   an   average   RMSE   of   0.2044.   The
PPSG  scheme’s  average  MAE  is  0.1184,  compared  to  the
AFL  scheme’s  average  MAE  of  0.1753,  further  verifying
the   superiority   of   the   PPSG   scheme.   Even   under   highly
imbalanced  data  distribution  conditions,  the  PPSG  scheme
performs  well.  The  UK-SMEC  dataset  is  clustered,  selecting
20  distant  stations  to  simulate  uneven  data  distribution.  As
shown  in  Fig.11,  the  PPSG  scheme  achieves  an  RMSE  of
0.3505, while the AFL scheme’s average RMSE is 0.4209, a
16.7%  reduction.  In  terms  of  MAE,  the  PPSG  scheme  has  a
Fig.  11.Comparing  PPSG  and  FedAsync  in  short-term  energy  prediction
accuracy under highly imbalanced data conditions.
value of 0.2355, whereas the AFL scheme’s average is 0.3547,
a 33.6% reduction.
Result  4:  On  real-world  smart  grid  dataset,  PPSG
demonstrates  high  accuracy  in  short-term  energy  con-
sumption    prediction,    validating    its    effectiveness    in
practical applications.
D.  Scalability and Large-Scale Performance Evaluation
To address RQ5, this section further evaluates the scalability
and overall performance of PPSG in large-scale node scenar-
ios.  To  this  end,  we  designed  three  experiments  examining
how  node  count  affects  model  accuracy  and  convergence,
blockchain  consensus  duration,  and  end-to-end  latency  under
varying network conditions. Building upon the aforementioned
Kubernetes  cluster,  up  to  1000  virtual  nodes  are  added  to
simulate smart grid scenarios of different scales. The topology
maintains  a  three-layer  architecture  consisting  of  the  device
layer, blockchain layer, and digital twin layer, utilizing a star
topology to simulate the typical communication mode between
the base station and each node.
1)  Impact of Node Quantity on Accuracy and Convergence
Performance:This  experiment  evaluates  the  system’s  scala-
bility  with  increasing  node  quantities  (20,  100,  500,  1000),
focusing  on  changes  in  model  accuracy  and  convergence
rounds across different datasets (MNIST, FMNIST, EMNIST)
with Non-IID setting.
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4180IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
Fig. 12.Comparing the impact of node quantity on accuracy and convergence performance across the MNIST, FMNIST, and EMNIST datasets.
Fig.  13.Comparing  the  impact  of  node  quantity  on  blockchain  consensus
time.
As shown in Fig.12, the results show that as the number of
nodes increases, the PPSG’s accuracy slightly decreases across
all datasets but remains at a high level (for example, accuracy
exceeds  95%  on  the  MNIST  dataset  with  1000  nodes).  At
the  same  time,  the  number  of  convergence  rounds  shows  a
moderate  increase  with  more  nodes,  with  a  gentle  upward
trend, indicating good scalability of PPSG. In comparison, the
baseline methods KAFL and DBAFL exhibit more significant
accuracy declines and slower convergence speeds under large-
scale   nodes.   This   verifies   PPSG’s   advantage   in   handling
large-scale,  heterogeneous  data  environments,  indicating  that
even with a substantial increase in smart grid nodes, the system
can  effectively  maintain  model  accuracy  and  convergence
speed.
2)  Impact   of   Node   Quantity   on   Blockchain   Consensus
Time:Under the MNIST dataset with a Non-IID setting, this
experiment analyzes the impact of increasing node quantities
(20,  100,  500,  1000)  on  the  time  cost  of  each  stage  in  the
blockchain consensus process.
As  shown  in  Fig.13,  results  indicate  that  as  the  number
of  nodes  increases,  the  total  blockchain  consensus  duration
significantly rises, from less than 1000 seconds with 20 nodes
to approximately 7000 seconds with 1000 nodes. Specifically,
the  time  cost  for  leader  station  election  grows  linearly  with
the  number  of  nodes  but  at  a  slower  rate,  indicating  that  the
election  algorithm  maintains  high  efficiency  with  large-scale
nodes.  The  duration  for  block  proposal  lengthens  with  more
Fig.   14.Comparing  end-to-end  average  latency   under  different   node
quantities  and  delay  conditions,  including  network  communication  time,
blockchain consensus delay, and model computation and aggregation time.
nodes,  but  the  impact  is  limited  due  to  the  committee  appli-
cation. The duration for verification and consensus attainment
increases significantly, reflecting the complexity of communi-
cation  and  verification  among  nodes.  The  cost  for  packaging
and  on-chain  is  controllable  despite  the  increase  in  nodes,
thanks  to  the  parallel  processing  advantage  of  station  nodes.
Overall, the PPSG maintains good blockchain performance in
large-scale  node  environments  through  the  committee  mech-
anism  and  efficient  consensus  algorithm  design,  ensuring  the
system’s security and reliability.
3)  Evaluation    of    Communication    Performance    Under
Different Scales and Delays:Under the MNIST dataset with
a   Non-IID   setting,   this   experiment   assesses   the   system’s
communication  performance  under  different  scales  (20,  100,
500, 1000 nodes) and different delay conditions (50ms, 100ms,
300ms),  distinguishing  between  computation  delay  and  com-
munication/consensus delay contributions.
As shown in Fig.14, the results show that with an increas-
ing  number  of  nodes,  the  end-to-end  latency  significantly
increases,  for  example,  under  a  50ms  delay  condition,  from
approximately  2  seconds  with  20  nodes  to  about  4  seconds
with 1000 nodes. For the same node quantity, network delay
significantly  affects  end-to-end  latency,  increasing  sequen-
tially under 50ms, 100ms, and 300ms conditions. Specifically,
network communication time is mainly influenced by network
delay   and   slightly   increases   with   the   number   of   nodes.
Consensus delay has a linear relationship with node quantity
and grows faster under high delay conditions. Model computa-
tion and aggregation time are influenced by node quantity and
computational  resource  allocation,  with  relatively  moderate
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4181
growth. Additionally, although system latency increases under
high delay conditions, blockchain operations and model train-
ing execute in parallel, preventing blockchain-induced delays
from fully affecting the model training process. This indicates
that the PPSG maintains high communication and computation
efficiency  even  when  facing  high  node  counts  and  complex
network  environments,  fully  adapting  to  the  demands  of  real
smart grid scenarios.
Result 5: In large-scale node scenarios, PPSG demon-
strates excellent scalability, stable performance, and high
model accuracy, and its convergence speed surpasses that
of the baseline algorithm.
## VI.  SYSTEMDEPLOYMENTCHALLENGES ANDFUTURE
## WORK
A.  Feasibility and Integration Challenges
This   study   validates   the   effectiveness   of   the   PPSG   in
smart  grid.  Experimental  results  demonstrate  its  excellent
scalability and performance under large-scale node conditions.
Specifically,  the  proposed  algorithm  exhibits  high  accuracy
in simulated environments, and the node scale is comparable
to  real-world  scenarios,  proving  its  potential  for  practical
applications.  However,  the  actual  deployment  of  smart  grid
still faces numerous challenges:
1)  UnreliableNetworkEnvironmentsandData
Synchronization:The  geographical  span  of  substations  and
transmission  lines  results  in  complex  network  environments,
which are prone to network jitter, packet loss, and high latency.
To  address  this  issue,  this  paper  introduces  a  “contribution-
based  random  election”  and  committee  mechanism  at  the
blockchain  layer.  High-quality  and  stable  nodes  are  selected
as  primary  block  producers,  while  offline  nodes  are  allowed
to  submit  local  models  upon  rejoining  the  network.  This
enhances the system’s tolerance to unstable networks.
2)  Resource  Adaptation  in  Heterogeneous  Environments:
Smart grid comprise various hardware devices with significant
differences   in  computational   power,   storage   capacity,   and
communication  bandwidth.  To  solve  the  resource  adaptation
problem,  it  is  recommended  to  deploy  protocol  conversion
gateways  at  the  device  layer,  utilizing  lightweight  logic  to
interface with common industrial protocols (such as OPC UA
and MQTT), thereby reducing the need for terminal hardware
upgrades.  Additionally,  for  terminal  devices  with  insufficient
computational  power,  proxy  training  can  be  conducted  on
edge  servers  to  improve  the  overall  system’s  computational
efficiency.
3)  InterfaceStandardsandMiddlewareSupport:
Currently,   widely   deployed   SCADA   systems   and   Energy
Management   Systems   (EMS)   in   smart   grid   lack   unified
standards   for   integration   with   digital   twin   platforms   or
blockchain  middleware. To achieve  effective integration, it is
advisable  to  add  standardized  interfaces  (such  as  OPC  UA
Server) between the digital twin layer and the device side or
employ cloud-based middleware for data protocol conversion.
This ensures that digital twin models can obtain real-time data
updates from various devices and sensors.
4)  Blockchain   Node   and   Operational   Costs:Deploying
blockchain requires installing corresponding services on core
nodes (such as substations and distribution rooms) and ensur-
ing  their  long-term  stable  operation.  Additionally,  bandwidth
overhead, storage space, and data privacy compliance must be
considered, especially in scenarios involving multi-party data
sharing across regional grid, where maintenance costs are high.
5)  Security:In  large-scale  node  environments,  the  system
is  more  susceptible  to  security  threats  such  as  Sybil  attacks,
DDoS  attacks,  and  node  spoofing.  To  enhance  system  secu-
rity,  anomaly  detection  and  rate-limiting  strategies  can  be
added   at   the   smart   contract   layer   to   temporarily   isolate
nodes that frequently submit abnormal or low-quality models.
Additionally, exploring combined on-chain and off-chain mali-
cious detection mechanisms and leveraging Trusted Execution
Environments  (TEE)  or  homomorphic  encryption  techniques
can further strengthen data and model privacy protection.
B.  Optimization Strategies for Asynchronous Federated
Learning in Large-Scale Heterogeneous Environments
(Future Work)
Although  this  paper  proposes  dual  dynamic  aggregation
factors  (i-MMD  and  NCTW)  at  the  algorithm  level  to  effec-
tively  address  data  distribution  discrepancies  and  model  lag
issues, there is still room for optimization in truly large-scale
and latency-distributed smart grid scenarios. Future work may
include:
1)  Adaptive   Learning   Rates   and   Delay   Feedback:In
situations where node updates are unsynchronized, introducing
adaptive  learning  rates  or  momentum  factors  based  on  delay
feedback can reduce the risk of model divergence and accel-
erate convergence speed.
2)  Segmented   Asynchronous   Updates:By   limiting   each
client to accept global model updates only after a certain num-
ber  of  local  iterations,  model  consistency  can  be  maintained
under asynchronous strategies. Combined with the latest model
version hashes recorded on the blockchain, the current model
versions used by each node can be accurately tracked, further
reducing model lag.
3)  LightweightModelsandIncrementalUpdates:
Adopting   lightweight   models   (such   as   distilled   networks,
pruning,   or   quantization   techniques)   can   reduce   network
transmission overhead. Additionally, recording model version
differences   (incremental   updates)   at   the   blockchain   layer
ensures  efficient  training  even  under  bandwidth  constraints
and limited device resources.
## C.  Deployment Pathways
To  apply  the  proposed  PPSG  system  to  actual  smart  grid
environments, the following deployment steps are feasible:
1)  Small-Scale Real-World Pilot:Deploy a limited number
of  blockchain  nodes  and  digital  twin  nodes  in  existing  smart
grid  pilot  or  demonstration  projects,  interfacing  with  current
network  devices  and  scheduling  systems  (SCADA/EMS).  By
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

## 4182IEEE TRANSACTIONS ON SMART GRID, VOL. 16, NO. 5, SEPTEMBER 2025
collecting data from the real environment, the system’s respon-
siveness   and   the   effectiveness   of   asynchronous   federated
learning in distributed state monitoring or fault diagnosis tasks
can be evaluated.
2)  Collaborative    Industrial    Partnerships    and    Testing
Platforms:Collaborate with grid companies or relevant indus-
tries to build large-scale simulation platforms (such as RTDS
or  OPNET).  These  platforms  should  replicate  issues  like
concurrent transmissions, topology changes, and node failures
in  large-scale  networks  while  maintaining  physical  model
accuracy, thereby validating the system’s stability and robust-
ness.
3)  Phased Deployment and Operation Maintenance:Select
specific  scenarios  (such  as  virtual  power  plant  aggregation,
electric  vehicle  charging  station  management,  or  distribution
network fault detection) to gradually verify the effectiveness of
the PPSG. During the gradual expansion, considerations must
include personnel training, operational maintenance costs, and
network  security  standards  to  ensure  the  system’s  long-term
stable operation in a commercial environment.
4)  Overall Feasibility and Stage-Based Deployment:Adopt
a   “partition-pilot-promotion”   strategy,   initially   conducting
pilots in local grid areas or microgrid environments to validate
the complete data flow from the device layer to the digital twin
layer and assess system performance. Subsequently, optimize
relevant  modules  and  gradually  expand  to  larger  backbone
networks or cross-regional grid to ensure the overall feasibility
and practicality of phased deployments.
Through  the  above  strategies,  the  PPSG  system  proposed
in  this  paper  will  achieve  more  robust  and  efficient  practical
applications  in  smart  grid,  further  promoting  the  intelligence
and security enhancement of smart grid.
## VII.  C
## ONCLUSION
Adaptive   Asynchronous   Federated   Learning   for   Digital
## Twin Driven Smart Grid
The PPSG system based on asynchronous federated learning
proposed  in  this  paper  effectively  addresses  data  distribu-
tion heterogeneity and model synchronization delays through
a   three-tier   architecture   design   (device   layer,   blockchain
layer,   and   digital   twin   layer).   Experimental   results   indi-
cate   that   the   proposed   method   maintains   high   learning
performance   and   system   scalability   even   in   large-scale
node  environments.  Although  numerous  challenges  exist  in
actual   deployment,   such   as   network   instability,   resource
heterogeneity,   interface   standardization,   and   system   secu-
rity,  solutions  like  protocol  conversion  gateways,  lightweight
blockchain   nodes,   and   layered   deployments   provide   high
feasibility.
Future  work  will  focus  on  further  optimizing  the  asyn-
chronous federated learning algorithm to enhance the system’s
adaptive  capabilities  and  robustness.  Additionally,  through
real-world pilot deployments and industrial collaborations, the
system’s  application  effectiveness  in  real  smart  grid  envi-
ronments  will  be  validated.  Ultimately,  this  research  aims
to  promote  the  widespread  application  of  PPSG,  achieving
efficient, secure, and intelligent grid management.
## R
## EFERENCES
[1]   I.-I.  Avramidis  and  G.  Takis-Defteraios,  “Flexicurity:  Some  thoughts
about  a  different  smart  grid  of  the  future,”IEEE  Trans.  Smart  Grid,
vol. 14, no. 2, pp. 1333–1336, Mar. 2023.
[2]   G. Cheng, Y. Lin, A. Abur, A. Gómez-Expósito, and W. Wu, “A survey
of  power  system  state  estimation  using  multiple  data  sources:  PMUs,
SCADA,  AMI,  and  beyond,”IEEE  Trans.  Smart  Grid,  vol.  15,  no.  1,
pp. 1129–1151, Jan. 2024.
[3]   F.  Arraño-Vargas  and  G.  Konstantinou,  “Modular  design  and  real-time
simulators  toward  power  system  digital  twins  implementation,”IEEE
Trans. Ind. Informat., vol. 19, no. 1, pp. 52–61, Jan. 2023.
[4]   A. Othman, G. Kaddoum, J. V. C. Evangelista, M. Au, and B. L. Agba,
“Digital twinning in smart grid networks: Interplay, resource allocation
and  use  cases,”IEEE  Commun.  Mag.,  vol.  61,  no.  11,  pp. 120–126,
## Nov. 2023.
[5]   B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from Decentralized
data,”  inProc.  20th  Int.  Conf.  Artif.  Intell.  Statist.  (AISTATS),  2017,
pp. 1273–1282.
[6]   P.  Kairouz  et  al.,  “Advances  and  open  problems  in  federated  learn-
ing,”Found.  Trends
## R
Mach.  Learn.,  vol.  14,  nos. 1–2,  pp. 1–210,
## Jun. 2021.
[7]   Z.  Zhou,  Y.  Tian,  J.  Xiong,  J.  Ma,  and  C.  Peng,  “Blockchain-enabled
secure  and  trusted  federated  data  sharing  in  IIoT,”IEEE  Trans.  Ind.
Informat., vol. 19, no. 5, pp. 6669–6681, May 2023.
[8]   X.  Ma  and  D.  Xu,  “TORR:  A  lightweight  blockchain  for  decen-
tralized  federated  learning,”IEEE  Internet  Things  J.,  vol.  11,  no.  1,
pp. 1028–1040, Jan. 2024.
[9]   M. Castro and B. Liskov, “Practical Byzantine fault tolerance,” inProc.
3rd Symp. Oper. Syst. Design Implement. (OSDI), 1999, pp. 173–186.
[10]  X.  Zhang,  X.  Zhu,  and  I.  Ali,  “Performance  analysis  of  IOTA  tangle
and a new consensus algorithm for smart grids,”IEEE Internet Things
J., vol. 11, no. 4, pp. 6396–6411, Feb. 2024.
[11]  P. Jain, J. Poon, J. P. Singh, C. Spanos, S. R. Sanders, and S. K. Panda,
“A digital twin approach for fault diagnosis in distributed photovoltaic
systems,”IEEE  Trans.  Power  Electron.,  vol.  35,  no.  1,  pp. 940–956,
## Jan. 2020.
[12]  P.   Moutis   and   O.   Alizadeh-Mousavi,   “Digital   twin   of   distribution
power  transformer  for  real-time  monitoring  of  medium  voltage  from
low  voltage  measurements,”IEEE  Trans.  Power  Del.,  vol.  36,  no.  4,
pp. 1952–1963, Aug. 2021.
[13]  L.  Xiao,  D.  Han,  C.  Yang,  J.  Cai,  W.  Liang,  and  K.-C.  Li,  “TS-
DP: An efficient data processing algorithm for distribution digital twin
grid  for  industry  5.0,”IEEE  Trans.  Consum.  Electron.,  vol.  70,  no.  1,
pp. 1983–1994, Feb. 2024.
[14]  S.  Zhang,  C.  Liu,  Y.-T.  Shi,  X.  Yin,  and  T.  Cheng,  “Grid-forming
inverter  primary  control  using  robust-residual-observer-based  digital-
twin  model,”IEEE  Trans.  Ind.  Informat.,  vol.  20,  no.  1,  pp. 638–648,
## Jan. 2024.
[15]  T.  Wang  and  Z.  Dong,  “Blockchain-based  clustered  federated  learning
for  non-intrusive  load  monitoring,”IEEE  Trans.  Smart  Grid,  vol.  15,
no. 2, pp. 2348–2361, Mar. 2024.
[16]  D. Qin, C. Wang, Q. Wen, W. Chen, L. Sun, and Y. Wang, “Personalized
federated  DARTS  for  electricity  load  forecasting  of  individual  build-
ings,”IEEE   Trans.   Smart   Grid,   vol.   14,   no.   6,   pp. 4888–4901,
## Nov. 2023.
[17]  A. Balint, H. Raja, J. Driesen, and H. Kazmi, “Using domain-augmented
federated  learning  to  model  thermostatically  controlled  loads,”IEEE
Trans. Smart Grid, vol. 14, no. 5, pp. 4116–4124, Sep. 2023.
[18]  K.  Yang,  W.  Chen,  J.  Bi,  M.  Wang,  and  F.  Luo,  “Multi-view  broad
learning system  for electricity  theft detection,”Appl. Energy, vol. 352,
Dec. 2023, Art. no. 121914.
[19]  T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated  optimization  in  heterogeneous  networks,”  inProc.  Mach.
Learn. Systemsk (MLSys), 2020, pp. 429–450.
[20]  S.  J.  Reddi  et  al.,  “Adaptive  federated  optimization,”  inProc.  9th  Int.
Conf. Learn. Represent. (ICLR), 2021, pp. 1–38.
[21]  W. Chen, K. Yang, Z. Yu, Y. Shi, and C. L. P. Chen, “A survey on imbal-
anced learning: Latest research, applications and future directions,”Artif.
Intell. Rev., vol. 57, no. 6, p. 137, 2024.
[22]  W.   Zhang,   Z.   Liu,   Y.   Jiang,   W.   Chen,   B.   Zhao,   and   K.   Yang,
“Self-balancing incremental broad learning system with privacy protec-
tion,”Neural Netw., vol. 178, Oct. 2024, Art. no. 106436.
[23]  L.  Feng,  Y.  Zhao,  S.  Guo,  X.  Qiu,  W.  Li,  and  P.  Yu,  “BAFL:  A
blockchain-based  asynchronous  federated  learning  framework,”IEEE
Trans. Comput., vol. 71, no. 5, pp. 1092–1103, May 2022.
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.

ZHANG et al.:  ADAPTIVE AFL FOR DT DRIVEN SMART GRID4183
[24]  K.  I.  Qureshi,  L.  Wang,  X.  Xiong,  and  M.  A.  Lodhi,  “Asynchronous
federated  learning  for  resource  allocation  in  software-defined  Internet
of  UAVs,”IEEE  Internet  Things  J.,  vol.  11,  no.  12,  pp. 20899–20911,
## Jun. 2024.
[25]  J.-H.  Chen,  M.-R.  Chen,  G.-Q.  Zeng,  and  J.-S.  Weng,  “BDFL:  A
Byzantine-fault-tolerance  decentralized  federated  learning  method  for
autonomous   vehicle,”IEEE   Trans.   Veh.   Technol.,   vol.   70,   no.   9,
pp. 8639–8652, Sep. 2021.
[26]  C. Xie, S. Koyejo, and I. Gupta, “Asynchronous federated optimization,”
2019,arXiv:1903.03934.
[27]  X. Wu and C.-L. Wang, “KAFL: Achieving high training efficiency for
fast-K asynchronous federated learning,” inProc. IEEE 42nd Int. Conf.
Distrib. Comput. Syst. (ICDCS), 2022, pp. 873–883.
[28]  J.  Ping,  Z.  Yan,  and  S.  Chen,  “A  privacy-preserving  blockchain-based
method  to  optimize  energy  trading,”IEEE  Trans.  Smart  Grid,  vol.  14,
no. 2, pp. 1148–1157, Mar. 2023.
[29]  W.  Hua,  Y.  Zhou,  M.  Qadrdan,  J.  Wu,  and  N.  Jenkins,  “Blockchain
enabled  decentralized  local  electricity  markets  with  flexibility  from
heating sources,”IEEE Trans. Smart Grid, vol. 14, no. 2, pp. 1607–1620,
## Mar. 2023.
[30]  U.   R.   Barbhaya,   L.   Vishwakarma,   and   D.   Das,   “ETradeChain:
Blockchain-based  energy  trading  in  local  energy  market  (LEM)  using
modified double auction protocol,”IEEE Trans. Green Commun. Netw.,
vol. 8, no. 1, pp. 559–571, Mar. 2024.
[31]  S.  Jiang,  J.  Li,  X.  Zhang,  H.  Yue,  H.  Wu,  and  Y.  Zhou,  “Secure
and privacy-preserving energy trading with demand response assistance
based  on  blockchain,”IEEE  Trans.  Netw.  Sci.  Eng.,  vol.  11,  no.  1,
pp. 1238–1250, Jan./Feb. 2024.
[32]  Y. Qu, S. R. Pokhrel, S. Garg, L. Gao, and Y. Xiang, “A blockchained
federated  learning  framework  for  cognitive  computing  in  industry  4.0
networks,”IEEE  Trans.  Ind.  Informat.,  vol.  17,  no.  4,  pp. 2964–2973,
## Apr. 2021.
[33]  H. Chai, S. Leng, Y. Chen, and K. Zhang, “A hierarchical blockchain-
enabled federated learning algorithm for knowledge sharing in Internet
of   Vehicles,”IEEE   Trans.   Intell.   Transp.   Syst.,   vol.   22,   no.   7,
pp. 3975–3986, Jul. 2021.
[34]  J.  Fattahi,  “A  federated  Byzantine  agreement  model  to  operate  Offline
electric  vehicle  supply  equipment,”IEEE  Trans.  Smart  Grid,  vol.  15,
no. 2, pp. 2004–2016, Mar. 2024.
[35]  M.  Shayan,  C.  Fung,  C.  J.  M.  Yoon,  and  I.  Beschastnikh,  “Biscotti:
A  blockchain  system  for  private  and  secure  federated  learning,”IEEE
Trans. Parallel Distrib. Syst., vol. 32, no. 7, pp. 1513–1525, Jul. 2021.
[36]  V.  Veerasamy,  L.  P.  M.  I.  Sampath,  S.  Singh,  H.  D.  Nguyen,  and
H.  B.  Gooi,  “Blockchain-based  Decentralized  frequency  control  of
Microgrids  using  federated  learning  fractional-order  recurrent  neural
network,”IEEE  Trans.  Smart  Grid,  vol.  15,  no.  1,  pp. 1089–1102,
## Jan. 2024.
[37]  C.  Xu,  Y.  Qu,  T.  H.  Luan,  P.  W.  Eklund,  Y.  Xiang,  and  L.  Gao,
“An  efficient  and  reliable  asynchronous  federated  learning  scheme  for
smart public transportation,”IEEE Trans. Veh. Technol., vol. 72, no. 5,
pp. 6584–6598, May 2023.
[38]  A. Gretton, K. M. Borgwardt, M. J. Rasch, B. Schölkopf, and A. Smola,
“A  kernel  two-sample  test,”J.  Mach.  Learn.  Res.,  vol.  13,  no.  1,
pp. 723–773, Mar. 2012.
[39]  A. Mondol, R. Gupta, S. Das, and T. Dutta, “An insight into Newton’s
cooling  law  using  fractional  calculus,”J.  Appl.  Phys.,  vol.  123,  no.  6,
pp. 1–10, Feb. 2018.
[40]  P. S. Efraimidis and P. G. Spirakis, “Weighted random sampling with a
reservoir,”Inf. Process. Lett., vol. 97, no. 5, pp. 181–185, Mar. 2006.
[41]  E. Androulaki et al., “Hyperledger fabric: A distributed operating system
for permissioned blockchains,” inProc. 13th EuroSys Conf. (EuroSys),
2018, pp. 1–15.
[42]  “Smartmeter    energy    consumption    data    in    London    households.”
Accessed: Jun. 15, 2023. [Online]. Available: https://data.london.gov.uk/
dataset/smartmeter-energy-use-data-in-london-households
Zhuoqun   Zhangreceived   the   B.S.   degree   of
information   sciences   in   computer   science   from
Massey  University,  New  Zealand,  in  2020.  He  is
currently  pursuing  the  Ph.D.  degree  in  cyberspace
security  with  the  Beijing  University  of  Posts  and
Telecommunications. His major interests are privacy
protection,   federated   learning,   and   homomorphic
encryption.
HaipengPengreceived    the    M.S.    degree    in
system  engineering  from  the  Shenyang  University
of   Technology,   Shenyang,   China,   in   2006,   and
the  Ph.D.  degree  in  signal  and  information  pro-
cessing   from   the   Beijing   University   of   Posts
and  Telecommunications,  Beijing,  China,  in  2010,
where    he    is    currently    a    Professor    with    the
School  of  Cyberspace  Security.  He  is  a  co-author
of   100   scientific   papers.   His   research   interests
include  compressive  sensing,  information  security,
network security, complex networks, and control of
dynamical systems.
Lixiang   Lireceived  the  M.S.  degree  in  circuit
and system from Yanshan University, Qinhuangdao,
China, in 2003, and the Ph.D. degree in signal and
information  processing  from  the  Beijing  University
of  Posts  and  Telecommunications,  Beijing,  China,
in  2006,  where  she  is  currently  a  Professor  with
the   School   of   Cyberspace   Security.   She   visited
the Potsdam Institute for Climate Impact Research,
Potsdam,  Germany,  from  July  2011  to  June  2012.
She  has  published  more  than  100  articles  and  a
monograph. Her research interests include compres-
sive  sensing,  complex  networks,  swarm  intelligence,  and  network  security.
She  is  the  Winner  of  the  National  Excellent  Doctoral  Thesis,  the  New
Century Excellent Talents in University, the Henry Folk Education Foundation,
the  Hong  Kong  Scholar  Award,  the  Beijing  Higher  Education  Program  for
Young Talents, and the Outstanding Youth Award of Chinese Association for
## Cryptology Research.
Shuang  Baoreceived  the  B.S.  degree  in  computer
science   and   technology   from   Shanxi   University,
Shanxi, China, in 2020. She is currently pursuing the
Ph.D. degree in cyberspace security with the Beijing
UniversityofPostsandTelecommunications,
Beijing,   China.   Her   major   interests   are   deep
learning,compressivesensing,andPrivacy
## Protection.
Authorized licensed use limited to: Vietnam National University. Downloaded on October 07,2025 at 14:23:59 UTC from IEEE Xplore.  Restrictions apply.