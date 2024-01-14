from manim import *

class IntroNeuralNetworks(Scene):
    def construct(self):
        # Title for the section
        title = Text("Introduction to Neural Networks", font_size=24)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Creating a basic neural network diagram
        neurons_layer1 = VGroup(*[Circle() for _ in range(3)]).arrange(RIGHT, buff=1)
        neurons_layer2 = VGroup(*[Circle() for _ in range(4)]).arrange(RIGHT, buff=1)
        neurons_layer3 = VGroup(*[Circle() for _ in range(2)]).arrange(RIGHT, buff=1)

        neural_network = VGroup(neurons_layer1, neurons_layer2, neurons_layer3).arrange(DOWN, buff=1)

        # Adding connections
        connections = VGroup()
        for layer1_neuron in neurons_layer1:
            for layer2_neuron in neurons_layer2:
                connections.add(Line(layer1_neuron.get_center(), layer2_neuron.get_center()).set_stroke(width=0.1))
        for layer2_neuron in neurons_layer2:
            for layer3_neuron in neurons_layer3:
                connections.add(Line(layer2_neuron.get_center(), layer3_neuron.get_center()).set_stroke(width=0.1))

        # Animating the neural network
        self.play(Create(connections), run_time=2)
        self.play(Create(neural_network), run_time=2)

        # Displaying text
        description = Text("A basic representation of a Neural Network with three layers.", font_size=18)
        self.play(Write(description))
        self.wait(2)
        self.play(FadeOut(description), FadeOut(neural_network), FadeOut(connections))

        # Transition to the next part
        # ...
