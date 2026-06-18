# Hack Computer from Scratch: Hardware & Software Bridge

A bottom-up implementation of a modern 16-bit computer system, starting from fundamental NAND gates and progressing up to building a custom virtual machine translator, compiler stack, and operating system. This project demonstrates a deep understanding of computer architecture, software compilation, and the seamless interface between hardware and software.

## 🏗️ System Architecture

The system is built in hierarchical layers, where each layer abstracts the complexity of the one beneath it.

### 1. The Hardware Layer (Digital Logic Design)
In this phase, I designed and implemented the entire chipset using Hardware Description Language (HDL).
* **Elementary Logic:** Implementation of all basic gates (AND, OR, XOR, Mux) starting solely from a NAND gate.
* **Arithmetic Logic Unit (ALU):** A 16-bit ALU capable of executing a variety of arithmetic and logical operations, forming the "brain" of the CPU.
* **Memory Hierarchy (Sequential Logic):** Construction of 16-bit registers and RAM modules (up to 16K) using Flip-Flops, managing state and data persistence.
* **Central Processing Unit (CPU):** Integration of the ALU, registers, and control logic to execute 16-bit instructions, manage memory access, and handle program flow.

### 2. The Low-Level Software Layer (Machine Language)
Exploring the hardware's capabilities through direct machine-level programming.
* **Instruction Set Architecture (ISA):** Mastery of the Hack binary format (A-instructions and C-instructions).
* **Low-Level Programming:** Development of assembly programs that interact directly with memory-mapped I/O (Screen and Keyboard).

### 3. The Assembler Layer (The Custom Assembler)
The software bridge developed to automate the hardware-software interface.
* **Python-Based Assembler:** A robust tool built from scratch in Python to parse symbolic assembly language and manage symbol tables.
* **Binary Generation:** Efficiently translates mnemonics into 16-bit binary code (machine language) executable by the Hack CPU.

### 4. The Virtual Machine Layer (Intermediate Code Translation)
Building the infrastructure for executing high-level code via a stack-based virtual machine architecture.
* **Stack Arithmetic:** Translates complex mathematical and logical expressions into stack-oriented Hack assembly commands.
* **Memory Management:** Implements dynamic mapping and synchronization between global and local virtual segments and physical RAM addresses.
* **Architecture:** Engineered using a strict modular approach featuring an independent instruction Parser and an optimized CodeWriter.

### 5. The Compiler Layer (High-Level Language)
Development of a full compiler for a high-level, object-oriented language (Jack).
* **Syntax Analysis:** Building a Tokenizer for lexical analysis and a Parser to generate a Parse Tree for structural validation.
* **Code Generation:** Translating high-level code into Virtual Machine (VM) language by traversing the Parse Tree.
* **Symbol Table Management:** Managing symbol tables to track variables (local, field, argument, static) and ensure proper memory allocation.

### 6. The Operating System Layer (System Libraries)
Implementation of a basic operating system library in the Jack language, bridging software and hardware.
* **Math Library:** Implementing algorithms for complex mathematical calculations (multiplication, division, square root).
* **Memory Management:** Managing dynamic memory (Heap) via allocation and deallocation of memory blocks.
* **I/O Drivers:** Developing drivers for screen display (drawing pixels, lines, and strings) and keyboard input.
* **System Services:** Providing core services that allow complex applications to run on the custom-built hardware.

---

## 📂 Repository Structure

* **`Hardware-Logic/`** - Implementation of combinational and sequential chips (HDL).
* **`Computer-Architecture/`** - The final CPU and Memory integration.
* **`Assembler/`** - Python source code for the symbolic-to-binary translator.
* **`VM-Translator/`** - Python implementation of the stack-based VM-to-Assembly backend.
* **`Compiler/`** - Implementation of the Jack compiler (Tokenizer, Parser, Code Generator).
* **`Operating-System/`** - Core OS libraries and system drivers.
* **`Assembly-Programs/`** - Low-level code samples and binary outputs.

---

## 🛠 Tech Stack

* **Hardware Description:** HDL
* **Software Stack:** Python 3
* **High-Level Language:** Jack
* **Low-Level Logic:** Hack Assembly
* **Simulation Tools:** Nand2Tetris Hardware Simulator, CPU Emulator & VM Emulator

---

## 📜 Acknowledgments
This project is based on the "Nand2Tetris" curriculum (The Elements of Computing Systems) by Noam Nisan and Shimon Schocken, as taught in The Hebrew University.
