# StatsBomb Open Data

Welcome to the StatsBomb Open Data repository. 

StatsBomb are committed to sharing new data and research publicly to enhance understanding of the game of Football. We want to actively encourage new research and analysis at all levels. Therefore we have made certain leagues of StatsBomb Data freely available for public use for research projects and genuine interest in football analytics. 

StatsBomb are hoping that by making data freely available, we will extend the wider football analytics community and attract new talent to the industry. We would like to collect some basic personal information about users of our data. By [giving us your email address](https://statsbomb.com/resource-centre/), it means we will let you know when we make more data, tutorials and research available. We will store the information in accordance with our Privacy Policy and the GDPR. 

Whilst we are keen to share data and facilitate research, we also urge you to be responsible with the data. Please register your details on https://www.statsbomb.com/resource-centre and read our [User Agreement](LICENSE.pdf) carefully.


## Terms & Conditions

By using this repository, you are agreeing to the [user agreement](LICENSE.pdf).

If you publish, share or distribute any research, analysis or insights based on this data, please state the data source as StatsBomb and use our logo:

![StatsBomb Logo](stats-bomb-logo.png)

## Getting Started

The [data](./data/) is provided as JSON files exported from the StatsBomb Data API, in the following structure:

* Competitions stored in [`competitions.json`](./data/competitions.json).
* Matches for each competition, stored in [`matches`](./data/matches/). Each file is named for a competition ID.
* Events and lineups for each match, stored in [`events`](./data/events/) and [`lineups`](./data/lineups/) respectively. Each file is named for a match ID.

Some documentation about the meaning of different events and the format of the JSON can be found in the [`doc`](./doc) directory.
