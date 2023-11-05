# <ins>Final</ins> <ins>Project</ins>
author: Lukáš Hrňa
# <ins>Final</ins> <ins>Project</ins>
author: Lukáš Hrňa

## Table of Contents
## Table of Contents

1. [About Project](#about-project)
2. [Technologies](#technologies)
3. [Final Product](#final-product)
4. [Installation](#installation)
5. [External Tutorials](#external-tutorials)
1. [About Project](#about-project)
2. [Technologies](#technologies)
3. [Final Product](#final-product)
4. [Installation](#installation)
5. [External Tutorials](#external-tutorials)

## About Project

This project combines Rust, Raylib, and PyTorch to create a maze and solve it using AI. It provides a visual representation of the maze and the AI's pathfinding.

## Technologies

- **Rust & Raylib**: The maze is generated using Rust and rendered with the Raylib library, providing an interactive visual experience.
  
 <sub>*Rust*</sub> :
  <sub>Programming language known for its strong memory safety guarantees and high performance. It prioritizes safety without sacrificing speed, making it a great choice for developing system-level software and applications where security and performance are critical.</sub>

 **<sub>*Raylib*</sub>** :
  <sub>C library for real-time 2D and 3D graphics rendering and game development. It's known for its simplicity and ease of use, making it a popular choice for indie game developers and hobbyists. Raylib provides a range of functions and features for graphics and game development, and it's known for being lightweight and efficient. It's typically used with the C or C++ programming languages but can be interfaced with other languages like Rust.</sub>

- **PyTorch**: An AI agent implemented in PyTorch navigates the maze to find the optimal path. You can choose different AI algorithms for pathfinding.
-- PyTorch:
Open-source deep learning framework primarily developed by Facebook's AI Research lab (FAIR). It's known for its flexibility and dynamic computational graph, which makes it a popular choice for researchers and developers in the field of machine learning and artificial intelligence. PyTorch provides a wide range of tools and libraries for building and training neural networks, and it has a large and active community that contributes to its growth and support.

- **Pygame**: popular open-source Python library used for developing 2D games, multimedia applications, and interactive simulations. It provides a range of functions and modules for game development, including graphics and sound, making it accessible for beginners and widely used in the game development community. Pygame is known for its simplicity and ease of use, making it a great choice for hobbyist game developers and educational purposes.(This was used for the first implementation of a maze generator, and it could potentially used for an actual project in the future. Here, it was just used as an example for future reference.)
  


## Final Product

The final product is an interactive maze solver that uses AI to find the optimal path through a generated maze.

## Installation

To get started with this project, follow these steps:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Hispalus1/AI-torch.git

2. **Python Environment**: Create a Python environment for PyTorch. You can do this using virtual environments in Python. Here's how:

   ```bash
   python -m venv maze-env
   source maze-env/bin/activate  # On Windows, use "maze-env\Scripts\activate"
   pip install -r requirements.txt

3. **Rust setup**: Setup maze-generator for AI to explore:
   ```bash
   cd rust-maze/source
   cargo build --release

## External Tutorials

Here are some external tutorials that can help you get started with the technologies used in this project:

- [Rust Programming Language Book](https://doc.rust-lang.org/book/)
- [Raylib Cheatsheet](https://www.raylib.com/cheatsheet/cheatsheet.html)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)

