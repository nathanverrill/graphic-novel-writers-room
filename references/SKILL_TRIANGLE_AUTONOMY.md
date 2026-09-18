---
name: triangle-autonomy
description: Grounded worldbuilding for autonomous technology in and around the South American lithium triangle (northern Chile, northwest Argentina, southwest Bolivia), now and in the near future (roughly 2030 to 2060). Covers AI, robotics, autonomous vehicles, drones, remote operations, sensors, and edge computing in mines, brine and DLE plants, logistics, water monitoring, security, borders, towns, herding, cooperatives, observatories, and data centers, plus the labor politics of automation, who owns the data, vendor geopolitics, how the environment breaks machines, local repair culture, and how communities, smugglers, and activists use the same tools. Hard sci-fi plausible only, with a cut list. Use whenever the user wants robots, AI systems, drones, autonomous trucks, remote control rooms, smart infrastructure, or surveillance tech in an Andean mining story, asks how automated a mine or town would be in a given year, or asks "would this be plausible." Companion to the other triangle skills and near-future-set-design.
---

# Autonomy in the Lithium Triangle

Uses the same plausibility labels as the companion skills. Follows the hard limits in near-future-set-design.

**"Lithium triangle" is only the name of the region here.** This skill is not about lithium. Treat lithium as one activity among many (copper, silver, tin, gold, borates, herding, farming, tourism, astronomy, trade, cities) and bring it in only when the writer's story does.

**This is a setting kit, not a plot.** It describes an environment, its constraints, and categories of things that can happen there. Do not steer toward any particular storyline, theme, protagonist, or political reading, and do not assume the writer wants conflict, villains, or a message. Serve whatever story the writer brings: a romance, a comedy, a procedural, a family saga, a thriller, a children's book. Offer options across the range rather than a favorite, and use only the parts that the writer's story touches.

## Plausibility labels

Everything here is labelled with the vocabulary defined in `SKILL_HARD_SF_RULES.md`: **T** truth,
**EG** educated guess, **S** speculation, **L** license, and **Cut** for what does not fit. The
rules for a license, the license log and the Thorne and Tyson tests are in that file; read it
before inventing anything the story then has to live with.

Here the "science" is engineering, the region's environment, and its labor and vendor politics.
Baseline is September 2026. Search before relying on a specific deployment, vendor, or regulation.

## The honest picture first

- **This region is already one of the most automated mining zones on Earth, and also one of the least.** A Chilean copper pit runs driverless 300 tonne trucks supervised from a tower in Santiago. Four hours away across the border, men push ore carts by hand and chew coca to get through a shift. Both are true in 2026 and both will be true in 2050. The gap is the story.
- **Autonomy arrives as retrofit.** Kits bolted onto existing trucks, sensors strapped to old pumps, a container of servers next to a 1990s plant. See the 80 / 15 / 5 rule in the set design skill.
- **Humans do not disappear. They move.** Out of the cab and into the control room, the maintenance bay, the contractor's yard, the city. Fewer, more skilled, further away, and less local.
- **The environment is the enemy.** Altitude, cold, UV, dust, salt, wind, and distance break machines faster than anywhere else. Whoever keeps things running has the power.
- **Connectivity is thin and politics can cut it.** Anything that matters has to work disconnected. That shapes every design.
- **Everyone gets the tools.** Companies, police, communities, activists, smugglers, thieves, and herders all fly drones and run models. No side has a monopoly for long.

## How the place breaks machines

Every piece of autonomous tech in a scene should show the marks of at least two of these.

| Condition | Effect | Visible response |
|---|---|---|
| **Altitude 2,300 to 5,000 m** | Thin air: drones lose lift and endurance, combustion engines lose a third of their power, fans move less air so electronics run hot, humans get slow and sick | Oversized props, bigger radiators and heat sinks, turbo or electric drive, oxygen in cabins and dorms, short drone sorties |
| **Day to night swing of 30 to 40 C** | Seals crack, condensation and ice inside housings, batteries sag at dawn, thermal cycling kills solder joints | Heated battery boxes, insulated enclosures, morning warm up routines, scheduled failures |
| **Extreme UV** | Plastics chalk and crumble, cable jackets split, camera domes yellow | Metal housings, sun shades, wrapped cables, everything faded |
| **Salt and brine** | The most corrosive industrial environment there is. Connectors rot, lidar windows crust over, salt creeps into everything | Stainless and fiberglass, sacrificial parts, daily wash downs, crusted white edges, grease on every terminal |
| **Dust and wind** | Abraded optics, clogged filters, static discharge, afternoon gales that ground drones | Air knives and wipers on sensors, filter stacks, grounding straps, flight windows at dawn |
| **Wet season on the salars (roughly January to March)** | Surface floods into a mirror. Salt crust softens. Vehicles bog or break through | Operations retreat to causeways and berms. Amphibious or tracked platforms. Seasonal shutdowns |
| **Lightning (altiplano summer)** | Kills masts, radios, and sensor networks | Lightning rods on everything, surge arrestors, spares on the shelf |
| **Distance** | Hours to the nearest parts depot or technician | On site printing and machining, cannibalized units, containers of spares, a culture of improvisation |
| **Radio quiet and dark sky rules near observatories** | Limits on transmitters, satellite terminals, and lighting for km around | Fiber where possible, shielded equipment, negotiated exceptions, quiet conflict |
| **Earthquakes** | Frequent and sometimes large | Seismic shutoffs, flexible pipe joints, fallen racks |

## Baseline 2026 (T)

**Chile.** Driverless haul trucks have run here since the late 2000s (Codelco's Gabriela Mistral was a world first for a whole fleet). Several big pits are now fully or largely autonomous. Remote integrated operations centers in Santiago and Antofagasta run pits, plants, and pipelines from hundreds of km away. Underground, loaders are tele operated from the surface at El Teniente and the new Chuquicamata underground. Autonomous drills, drone survey, predictive maintenance, and AI ore sorting are routine. Unions have negotiated hard over job losses and retraining. Nationally: an AI policy, a data center boom around Santiago with court fights over water, and a regional open language model project. Satellite internet is common in remote sites.

**Argentina.** New lithium plants are being built with modern control systems from day one, but the workforce, regulators, and supply chain are newer to it. Autonomous haulage is planned for the big copper projects in San Juan. National government talks up AI and has courted hyperscale data center investment in Patagonia. Provinces buy surveillance systems on their own; Jujuy installed a Chinese built one years ago.

**Bolivia.** State plants have had trouble running at all, let alone autonomously. Cooperatives use jackhammers, dynamite, and hand sorting. Connectivity outside cities is poor; satellite internet licensing has been a political football. Phones, QR payments, WhatsApp, and Facebook are nonetheless universal, and cheap Chinese drones are everywhere.

**Everywhere.** Spanish language AI is excellent. Quechua and Aymara are low resource but improving through community and university projects. Kunza is a revival language with almost no data.

## By domain

### Open pit and underground mines
- Autonomous haul trucks, drills, dozers, water carts, and graders in a geofenced pit. Humans in light vehicles are the hazard the system is built around (T).
- Trolley assist and battery or hybrid trucks replacing diesel, partly because engines suffer at altitude (EG).
- Block cave mines run almost entirely by tele operation and automation, because the ground is too dangerous (T to EG).
- Autonomous trains or platooned trucks to the coast (EG; precedent in Australia).
- Robotic tire changers, refuelers, and inspection crawlers. Legged robots doing rounds in plants and tunnels (T in pilots, EG routine).
- AI dispatch, geology models, grade control, blast design, and predictive maintenance. The mine that feeds AI is run by it (T).
- Still human: blasting crews, maintenance, surveying edge cases, emergency response, anything after an earthquake (T through EG).

### Brine operations and chemical plants
- Well fields with sensor packed pumps reporting level, flow, density, and chemistry. Autonomous valve control balancing extraction against permit limits (T to EG).
- Drone and satellite monitoring of pond levels, liner leaks, salt harvest progress. Autonomous salt harvesters on ponds are plausible because it is flat, repetitive, and corrosive (EG).
- DLE plants are chemical plants: highly automated by nature, run by a small shift crew and a remote control room (T).
- Robotic sampling and an automated lab, because assays at altitude on night shift are error prone (EG).
- Reinjection monitoring with AI models of the aquifer. The model is contested; see "Who owns the data" (EG).

### Logistics
- GPS tracked convoys with jamming detection (T). Driver assist and fatigue monitoring in every cab (T).
- Driverless trucks on the fixed desert highway runs between plant and port, with humans for the mountain passes, towns, and border posts (EG). Fully driverless across a border crossing (S).
- Truckers are organized and can shut roads. Automation of trucking is the most politically explosive automation in the region (EG conflict).
- Cargo drones for samples, parts, and medical supplies between camps (EG). Not for bulk.
- Automated port terminals at Mejillones and Antofagasta (EG).

### Water and environment
- Dense sensor networks: piezometers, flow gauges, weather stations, vegetation indices from satellite, flamingo counts by drone and computer vision (T to EG).
- **Two networks, two truths.** Company telemetry and community or university sensors measure the same basin and disagree. Each side has its own model (T, intensifying EG).
- Public dashboards demanded by courts and lenders. Arguments over raw data access, calibration, and who pays the hydrologist (EG).
- Autonomous leak detection on desalination pipelines, which double as intrusion detection (EG).

### Security and policing
See the security skill. In brief: tower cameras, radar, thermal, scheduled drone patrols, plate readers on the only road, facial recognition at gates and in provincial capitals, social media scraping, counter drone jammers, satellite change detection (T to EG). Autonomous ground patrol vehicles on perimeters (EG). Armed autonomous systems (Cut for private actors, S at most for a military border post as a remotely operated, human fired weapon).

### Borders and smuggling
- Chile's northern border: sensor towers, drones, trenches, army patrols (T).
- Smugglers use drones for scouting and small high value loads, encrypted apps, cheap satellite terminals, GPS tracks shared like fishing spots, and vehicles with cloned plates (T to EG).
- Driverless or remotely driven smuggling vehicles across open salt (S). Plausible because the terrain is flat and empty, limited because goods are bulky and vehicles are worth more than drivers.
- Ore thieves with thermal scopes, drones to watch guards, and insiders who switch off a camera (T to EG).

### Towns and services
- Telemedicine with remote specialists, AI triage on a nurse's tablet, drone delivery of blood tests and medicines to posts hours from a hospital (EG).
- AI tutors and translated curricula on phones; the limit is connectivity and power, then teachers' unions (EG).
- Government by chatbot: permits, benefits, complaints. Works in Chile, patchy in Argentina, aspirational in Bolivia (EG).
- Payment apps and QR everywhere already (T). See the money skill.
- Municipal water rationing run by smart valves, which makes the rationing schedule a hackable, protestable thing (EG).
- Most homes have no robots. A few have a vacuum. Solar, a battery, a satellite dish, and phones are the household tech (T to EG).

### Herding, farming, salt
- GPS collars on llamas and sheep, virtual fencing, drones to find animals and scare foxes and pumas (EG).
- Satellite pasture and wetland monitoring used by herders as evidence against the mine (EG).
- Quinoa and salt harvesting stay mostly manual or small tractor. Margins do not pay for robots (T through EG).

### Cooperatives and informal mining
- Almost no automation. Cheap drones, phones, WhatsApp groups, handheld XRF analyzers to check ore grade before selling, metal detectors, pirated mine planning software (T to EG).
- Ore buyers use AI assays and price feeds the miners cannot see. Information asymmetry is the exploitation (EG).
- Remote controlled or robotic mining inside Cerro Rico type workings: proposed by outsiders for safety, resisted by cooperatives because it removes the members (S as a fight, not a deployment).

### Communities and activists
- Drones, satellite imagery subscriptions, open source mapping, their own sensor networks, lawyers who file data access requests, and students who can read a telemetry log (T to EG).
- AI translation in consultation meetings between Spanish, Quechua, Aymara, Mandarin, and English. Useful, distrusted, and a new place for disputes about what was agreed (EG).
- Community language models trained on elders' recordings, run locally because people do not want the data leaving (EG to S).
- Deepfakes and AI generated smear campaigns against leaders, and against executives. Everyone learns to distrust video, which also helps real abusers deny real footage (EG).
- Livestream remains the main weapon. Jamming or throttling during a crackdown is the main counter (T to EG).

### Observatories and data centers
- The Atacama's telescopes are some of the most automated scientific instruments on Earth, producing data volumes that need AI to sift. They need radio silence and dark skies, which puts them at odds with mines, satellite constellations, and towns (T).
- Solar powered data centers in the desert are plausible: best sun on the planet, cold nights for cooling, fiber to the coast. The limits are water, transmission lines, earthquakes, and politics (EG).
- "The minerals leave, the compute stays somewhere else" is a standing grievance. A sovereign compute demand, a share of capacity for national or regional use, is a plausible bargaining chip (EG to S).

## Where the computing lives

- **On site and disconnected by design.** A pit cannot stop because a satellite link dropped or a blockade cut the fiber. Autonomy stacks run on ruggedized servers in containers and on the vehicles themselves. The remote center supervises; it does not drive (T).
- **Links:** private LTE or 5G bubble over the site, microwave hops, fiber along the pipeline or power line, satellite as backup. One fiber route is a single point of failure that everyone local knows about (T to EG).
- **Small models at the edge, big models far away.** Inspection robots, cameras, and wearables run local models. Planning, geology, and corporate analytics run in a cloud region in Santiago, São Paulo, or abroad (EG).
- **Sovereignty fights:** where mine data, water data, and biometric data are stored; whether a Chinese, US, or European stack runs the plant; whether the state can inspect the code that decides how much brine is pumped (EG).
- **Bolivia** insists on state control on paper and lacks the capacity in practice, so foreign vendors run black boxes inside state plants (EG).

## Vendor geopolitics

- Western mining majors run Western and Japanese autonomy systems (Caterpillar, Komatsu, Sandvik, Epiroc, Hexagon and similar), Western cloud, and compliance heavy data practices.
- Chinese operators bring Chinese trucks, drones, cameras, control systems, telecom gear, and cloud. Cheaper, faster to deploy, serviced by flown in technicians.
- Provinces and police buy whichever vendor finances the deal.
- Pressure from Washington and Beijing over telecom and surveillance gear is constant. A change of government can mean ripping out a network (T to EG).
- Lock in is real: whoever supplied the autonomy system effectively controls the mine's ability to run. Remote license suspension during a dispute is plausible (EG to S).

## Labor and politics of automation

- **Fewer local jobs per tonne, every year.** Jobs were the main promise to communities. When the jobs are in a control room 1,000 km away, the bargain shifts to royalties, contracts, and per tonne payments (T to EG).
- **Unions fight it and shape it.** Strong in Chilean copper: no layoff clauses, retraining funds, bonuses for accepting autonomy. Subcontracted workers get none of that (T).
- **Who benefits:** the remote workforce is more urban, more educated, and more female than the pit ever was. Mining towns lose the wage; cities gain it (T to EG).
- **New local work:** sensor cleaning, robot wrangling, drone piloting, maintenance, environmental monitoring, data labeling, security. Lower paid than the truck driver's job it replaced, unless the community company captures the contract (EG).
- **Safety is the honest argument.** Fewer people killed by trucks, rockfalls, and altitude. Companies lead with it; unions know it is true; it still costs jobs (T).
- **Sabotage and slowdown:** cones in front of a driverless truck, a blocked sensor, a work to rule by the maintenance crew everyone depends on (EG).
- **Bolivia's cooperatives are the counter case:** a labor system that absorbs people instead of shedding them, at terrible human cost (T).
- **Accountability gap:** when an autonomous truck kills a contractor or a control algorithm over pumps an aquifer, responsibility disappears among operator, vendor, integrator, and remote supervisor (EG).

## How it fails (use these)

- Lidar blinded by salt crust or blowing dust; trucks stop in a line and wait for a human with a rag.
- Dawn battery sag strands a drone on the salar.
- Flooded salt surface swallows an autonomous harvester to the axles.
- Lightning takes out the sensor mast the court ordered installed.
- A software update pushed from another continent at 3 am bricks the dispatch system.
- Fiber cut by a blockade, a backhoe, or an earthquake; site falls back to local mode and the remote center watches a frozen screen.
- GPS jamming by cargo thieves confuses a convoy.
- A vicuña herd, a flamingo flock, or a religious procession is not in the training data.
- The model says the aquifer is fine. The spring is dry.
- A vendor dispute or sanction freezes licenses and spares.
- A technician with a laptop and a grudge.
- A cheap sensor drifts for two years and nobody checks, because the dashboard is green.

And how it gets fixed: the local mechanic who learned on YouTube and keeps a foreign robot alive with printed parts and wire; the WhatsApp group of technicians across three countries; the container of cannibalized units; the old timer who can still drive the truck manually.

## Near future summary by decade

| Era | What it looks like |
|---|---|
| **2030s** | Chilean and new Argentine mega mines largely autonomous in the pit. DLE plants remote supervised. Drones routine for everyone. Satellite internet in every camp and many villages. First driverless desert highway runs. Bolivian plants finally operating with foreign black box control systems. Community sensor networks in every contested basin |
| **2040s** | Inspection and maintenance robots common. Truck driving as a mining job mostly gone in Chile. Control rooms partly automated themselves; one supervisor oversees what ten did. Trucker conflicts over automated corridors. AI mediated consultation and translation normal and distrusted. Desert data centers exist. Deepfake politics routine |
| **2050s** | Older sites run by skeleton crews plus contractors. Closure and cleanup done by machines nobody wanted to pay humans for. Cooperatives still digging by hand next door. Knowledge of how to run things manually is rare and valuable. The main arguments are about data, royalties, and who is accountable |

## Cut list

These fail the Thorne test for this setting. Any of them can still be used as a declared **License** under the rules above, never by accident.

- General purpose humanoid robots doing mine labor. Wheels, tracks, arms on rails, quadrupeds, and drones do the work.
- Fully unmanned mines or plants. Maintenance, blasting, emergencies, and politics need people.
- A single AI running a mine, a company, or a province as a character with intentions. It is many narrow systems from many vendors that do not talk to each other well.
- Drone swarms darkening the sky. Thin air, wind, cold, and battery limits keep fleets small and flights short.
- Private armed robots or autonomous weapons at mine sites.
- Flawless surveillance. A few roads and gates are covered; the rest is empty, and sensors fail.
- Robots in ordinary homes beyond appliances.
- Bolivia leapfrogging to a high tech mining sector on its own. Foreign run systems inside state shells is the plausible form.
- Cooperatives automating. Their economics are people.
- Instant rollout. Every deployment is years late, over budget, and retrofitted.
- Tech that works the same here as at sea level. If it has not been adapted for altitude, salt, and cold, it is broken.
- Automation ending conflict. It moves the conflict from jobs to data, royalties, water, and accountability.

## Output formats

Same as the companion skills (**world brief**, **location sheet**, **faction sheet**, **plausibility review**, **timeline**). Add:

**Autonomy stack:** for any site or town in a given year, list what is autonomous, what is remote operated, what is still manual and why, where the compute sits, what the links are and their single points of failure, which vendors and whose cloud, who maintains it, who owns the data, what the environment has done to it, and what happens when it goes offline.

**Failure scene:** a specific breakdown with cause, who notices first, who can fix it, how long it takes, and what it costs or reveals.

**Day in the life:** a shift for a remote operator in the city, a maintenance tech on site, a community monitor, a trucker being automated out, or a cooperative miner next door, showing how each touches the same systems.

**Plausibility review:** tag each piece of tech T, EG, S, or Cut for the chosen year and country, and offer the nearest plausible substitute.

**License log:** a running list for the project. For each L: what it is, the story reason, the nearest T, EG, or S version, what must stay rigorous around it, and whether it is the premise, a small license, or L clarity. Show the log whenever a plausibility review is given, and warn when the count is getting high.

## Keep current

Search before relying on: which mines run autonomous fleets and whose systems; union agreements on automation in Chile; satellite internet licensing in Bolivia; data center projects and water rulings in Chile and Argentina; provincial and police surveillance procurement; drone and AI regulation in each country; regional language model projects and indigenous language AI; any incidents involving autonomous equipment.

Sources: Cochilco and Consejo Minero technology reports, company sustainability and technical reports, Minería Chilena, BNamericas, Mining.com, union statements, CENIA (Chile), Fundación Sadosky (Argentina), Derechos Digitales and Access Now on surveillance, Citizen Lab, ESO and ALMA on radio quiet zones, academic work on automation and labor in Chilean mining.
