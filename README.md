# MDVRPTW-Solomon

<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/israelpereira55/MDVRPTW-Solomon">
    <img src="images/mona-lisa100K.gif" alt="Logo" width="500" height="500">
  </a>

  <h3 align="center">Let's solve the MDVRPTW!</h3>

  <p align="center">
    This is an algorithm that seeks to get the optimum solutions for the MDVRPTW. 
    <br />
    It is under development and research.
    <br />
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

The Vehicle Routing Problem (VRP) is a known combinatorial problem for it's difficult. On this project, we seek to solve the Multi Depot Vehicle Routing Problem with Time Windows (MDVRPTW) which is harder!. 

First we use a set of cluster methods to clusterize the depots and after that the Solomon I1 Insertion Heuristic is used to construct the initial solution. And then... WIP =).



### Clustering Methods

This section should list any major frameworks that you built your project using. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.
* [K-Means]
* [Urgencies](https://jquery.com)



<!-- GETTING STARTED -->
## Getting Started

First you need a MDVRPTW problem instancy, which you can get on VRP Libraries.
We will list some libraries in which you can get them. We have the "instances" folder with Cordeuat and Vidal MDVRPTW instances, mostly for backup purposes but You can use them too!

You can also make your own instance, but it needs to follow Cordeaut standards. 

* [VRP-REP](http://www.vrp-rep.org/variants/item/mdvrptw.html)
* [NEO LCC](https://neo.lcc.uma.es/vrp/vrp-instances/multiple-depot-vrp-instances/)

### Prerequisites

Python 3.6 or higher is required.


### Installation

1. Get the dependencies
   ```sh
   python -m pip install -r requirements.txt
   ```
2. Run the project
   ```sh
   python main.py <FLAGS>
   ```



<!-- USAGE EXAMPLES -->
## Flags description

Here we describe the algorithm parameters.

- **(Obrigatory)**
    - --instance 
        - path for the MDVRPTW instance.

- **(Optional)**
    - --cluster _Default: kmeans_
        - Options: (kmeans/urgencies)


* Example of usage:
   ```
   python main.py --instance ./instances/cordeau-al-2001-mdvrptw/pr01.txt --cluster kmeans
   ```


<!-- CONTACT -->
## Contact

Israel - israelpereira55@gmail.com

Project Link: [https://github.com/israelpereira55/MDVRPTW-Solomon](https://github.com/israelpereira55/MDVRPTW-Solomon)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* [Best README Template](https://github.com/israelpereira55/MDVRPTW-Solomon)


## References

[1] Cordeau, Jean-François, Gilbert Laporte, and Anne Mercier. "A unified tabu search heuristic for vehicle routing problems with time windows." Journal of the Operational research society 52.8 (2001): 928-936.

[2] Giosa, I. D., I. L. Tansini, and I. O. Viera. "New assignment algorithms for the multi-depot vehicle routing problem." Journal of the operational research society 53.9 (2002): 977-984.




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/israelpereira55/MDVRPTW-Solomon.svg?style=for-the-badge
[contributors-url]: https://github.com/israelpereira55/MDVRPTW-Solomon/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/israelpereira55/MDVRPTW-Solomon.svg?style=for-the-badge
[forks-url]: https://github.com/israelpereira55/MDVRPTW-Solomon/network/members
[stars-shield]: https://img.shields.io/github/stars/israelpereira55/MDVRPTW-Solomon.svg?style=for-the-badge
[stars-url]: https://github.com/israelpereira55/MDVRPTW-Solomon/stargazers
[issues-shield]: https://img.shields.io/github/issues/israelpereira55/MDVRPTW-Solomon.svg?style=for-the-badge
[issues-url]: https://github.com/israelpereira55/MDVRPTW-Solomon/issues
[license-shield]: https://img.shields.io/github/license/israelpereira55/MDVRPTW-Solomon.svg?style=for-the-badge
[license-url]: https://github.com/israelpereira55/MDVRPTW-Solomon/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
