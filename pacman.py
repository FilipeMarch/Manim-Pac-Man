class PacmanGame(Scene):
    def construct(self):
        # Pacman is going right by default
        self.pacman_direction = RIGHT

        # Pacman has an initial velocity of 0.1
        self.pacman_velocity = 0.1

        # Tracking how much time has elapsed on the clock
        self.elapsed_time = 0

        # When the player presses the arrows, it changes the direction of Pacman by rotating it. Initially the rotation is 0.
        self.pacman_rotation = 0

        # How frequently the pacman mouth opens and shuts
        self.open_mouth_frequency = .25

        # The current state of the mouth
        self.open_mouth = False

        # How many food the pacman has eaten
        self.number_of_food_collected = 0

        # The highest score of the user
        self.highest_score = 0

        # The sound that plays when the pacman eats a food
        self.music = pyglet.media.load('sounds/1.wav', streaming=False)

        # The score of the player is a text and a number
        text = Tex('Score: ').to_corner(DL, buff=0.14)
        score = DecimalNumber(0, 1).next_to(text, RIGHT)

        # The button the user has to click to initiate the game
        self.start = Tex('START')
        self.surround_start = SurroundingRectangle(self.start, buff=0.42)

        # The name of the game
        self.pacman_text = Tex('Pac-Man').scale(3).to_edge(UP)

        # Creating the name of the game, and the start button
        self.play(FadeIn(self.pacman_text))
        self.play(Write(self.surround_start), Create(self.start))

        # The user has to click the button to start the game
        self.interactive_embed()

        # When the user clicks the start button, the game starts
        self.play(Write(text), Write(score))

        # The pacman has two different mouths, a closed mouth and an open mouth
        shut_mouth_pacman = AnnularSector(inner_radius = 0, outer_radius = 1, angle = 360*DEGREES, start_angle = 0).set_fill(YELLOW).set_stroke(color = WHITE, width = 1.4)
        open_mouth_pacman = AnnularSector(inner_radius = 0, outer_radius = 1, angle = 315*DEGREES, start_angle = 0).set_fill(YELLOW).set_stroke(color = WHITE, width = 1.4)
        
        pacman_eye = Circle(radius = 0.1, color=BLACK).set_fill(BLACK, 1)

        # Create the Pac-Man
        self.pacman = shut_mouth_pacman.copy()
        self.play(Create(self.pacman), Write(pacman_eye))

        # Updating the pacman's eye position
        pacman_eye.add_updater(
            lambda m: m.move_to(self.pacman.get_center() + 0.42*UP + 0.42*RIGHT)
        ) 

        def update_elapsed_time(pacman, dt):
            """
            It updates the pacman's mouth, which opens and closes,
            and updates the pacman's position if he goes beyond the screen
            and checks if the user has lost the game
            """
            self.elapsed_time += dt
            # Checking if the mouth should be open or closed
            if self.elapsed_time > self.open_mouth_frequency:
                self.elapsed_time = 0
                if self.open_mouth:
                    self.open_mouth = False
                    new_pacman = shut_mouth_pacman.copy().move_to(self.pacman).rotate(self.pacman_rotation).set_width(self.pacman.get_width())
                    self.pacman.become(new_pacman)
                else:
                    self.open_mouth = True
                    new_pacman = open_mouth_pacman.copy().move_to(self.pacman).rotate(self.pacman_rotation).set_width(self.pacman.get_width())
                    self.pacman.become(new_pacman)

            # Checking if the Pac-Man has gone beyond the scene frame and updating its position accordingly
            if self.pacman.get_edge_center(RIGHT)[0] < -7 and list(self.pacman_direction) == list(LEFT):
                self.pacman.move_to(self.pacman.get_center() + (14+self.pacman.get_width())*RIGHT )
            elif self.pacman.get_edge_center(LEFT)[0] > 7 and list(self.pacman_direction) == list(RIGHT):
                self.pacman.move_to(self.pacman.get_center() + (14+self.pacman.get_width())*LEFT )
            elif self.pacman.get_edge_center(UP)[1] < -4 and list(self.pacman_direction) == list(DOWN):
                self.pacman.move_to(self.pacman.get_center() + (8+self.pacman.get_width())*UP )
            elif self.pacman.get_edge_center(DOWN)[1] > 4 and list(self.pacman_direction) == list(UP):
                self.pacman.move_to(self.pacman.get_center() + (8+self.pacman.get_width())*DOWN )

            # Verifying if the pacman is too small, then the player lost
            if self.pacman.get_width() < .742:
                # Create the highest score text
                highest_score_text = Tex('Highest Score: ').to_edge(RIGHT, buff=1.5).to_edge(DOWN)
                highest_score_number = DecimalNumber(self.highest_score, 1).next_to(highest_score_text, RIGHT)
                self.add(highest_score_text, highest_score_number)
                # Diminish opacity for all mobs in scene
                for mob in self.mobjects:
                    mob.set_opacity(0.5)
                    mob.clear_updaters()
                # Show game over
                text = Tex('Game Over').scale(3).to_edge(UP)
                self.play(Write(text))

                # The button the user has to click to initiate the game
                self.start = Tex('START')
                self.surround_start = SurroundingRectangle(self.start, buff=0.42)
                self.add(self.surround_start, self.start)

        # Adding the updater to the pacman
        self.pacman.add_updater(update_elapsed_time)
        
        # Updating the position of the pacman for every frame
        def update_pacman_position(pacman, dt):
            pacman.shift(self.pacman_direction*self.pacman_velocity)

        self.pacman.add_updater(
            update_pacman_position
        )

        # Each good food is a RED square
        def create_random_food():
            return Square(color='#E92B47', fill_color='#E92B47', fill_opacity=1).scale(0.14).move_to(random.uniform(-4,4)*UP+random.uniform(-4,4)*RIGHT)

        # Updater for the bad food, which is an ORANGE square
        def check_bad_food_collision_with_pacman(mobject, dt):
            """
            Checks the opacity of the bad food,
            and if it is 0, then it is removed from the scene

            If it is not 0, then it is checked if it collides with the pacman
            if it does, then the player loses points, the food is removed from the scene,
            and the pacman becomes smaller
            """
            if mobject.get_opacity() <= 0:
                mobject.clear_updaters()
                self.foods.remove(mobject)
                return

            intersection = Intersection(self.pacman, mobject)
            if intersection.width > 0 and intersection.height > 0:
                self.remove(mobject)
                self.number_of_food_collected -= 0.5
                score.set_value(self.number_of_food_collected)
                self.pacman.set_width(self.pacman.get_width()-0.05)

        # Updater for the good food, which is a RED square
        def check_good_food_collision_with_pacman(mobject, dt):
            """
            Checks if the good food collides with the pacman,
            if it does, then the player gains points, the food is moved to another place on the scene,
            and the pacman becomes bigger. Also, a sound is played.

            For every 10 points, the speed of the pacman is increased, and its open mouth frequency 
            is decreased. It also creates 10 new bad food, which disappear after a certain amount of time.
            """
            intersection = Intersection(self.pacman, self.food)
            if intersection.width > 0 and intersection.height > 0:
                self.food.move_to(random.uniform(-4,4)*UP+random.uniform(-4,4)*RIGHT)
                self.pacman.set_width(self.pacman.get_width()+0.1)
                self.number_of_food_collected += 1
                score.set_value(self.number_of_food_collected)
                if self.number_of_food_collected > self.highest_score:
                    self.highest_score = self.number_of_food_collected

                self.music.play()

                if score.get_value() % 10 == 0 or score.get_value() % 10 == 0.5:
                    self.pacman_velocity += 0.1
                    self.open_mouth_frequency -= 0.01
                    self.foods = Group(
                        *[create_random_food().add_updater(
                            check_bad_food_collision_with_pacman).add_updater(
                            lambda m, dt: m.set_opacity(m.get_opacity()-0.01)
                        ).set_color(ORANGE) for i in range(10)
                            ]
                    )
                    self.add(self.foods)
                    self.pacman.set_width(
                        self.pacman.get_width()-.42
                    )

        self.food = create_random_food()
        self.food.add_updater(
            check_good_food_collision_with_pacman
        )
        self.add(self.food)

        self.interactive_embed()

    def on_key_press(self, symbol, modifiers):
        """
        Decides what happens when the user presses the arrow UP, DOWN, LEFT, RIGHT keys.
        Normally it just changes the direction of the pacman, and save its rotation state.
        """
        if symbol == pyglet_key.UP:
            if list(self.pacman_direction) == list(RIGHT):
                self.pacman.rotate(90*DEGREES)
            elif list(self.pacman_direction) == list(LEFT):
                self.pacman.rotate(-90*DEGREES)
            elif list(self.pacman_direction) == list(DOWN):
                self.pacman.rotate(180*DEGREES)

            self.pacman_rotation = 90*DEGREES
            self.pacman_direction = UP

        if symbol == pyglet_key.DOWN:
            if list(self.pacman_direction) == list(RIGHT):
                self.pacman.rotate(-90*DEGREES)
            elif list(self.pacman_direction) == list(LEFT):
                self.pacman.rotate(90*DEGREES)
            elif list(self.pacman_direction) == list(UP):
                self.pacman.rotate(180*DEGREES)

            self.pacman_rotation = -90*DEGREES
            self.pacman_direction = DOWN

        if symbol == pyglet_key.LEFT:
            if list(self.pacman_direction) == list(UP):
                self.pacman.rotate(90*DEGREES)
            elif list(self.pacman_direction) == list(DOWN):
                self.pacman.rotate(-90*DEGREES)
            elif list(self.pacman_direction) == list(RIGHT):
                self.pacman.rotate(180*DEGREES)
            
            self.pacman_rotation = 180*DEGREES
            self.pacman_direction = LEFT
            
        if symbol == pyglet_key.RIGHT:
            if list(self.pacman_direction) == list(UP):
                self.pacman.rotate(-90*DEGREES)
            elif list(self.pacman_direction) == list(DOWN):
                self.pacman.rotate(90*DEGREES)
            elif list(self.pacman_direction) == list(LEFT):
                self.pacman.rotate(180*DEGREES)

            self.pacman_rotation = 0*DEGREES
            self.pacman_direction = RIGHT
        
        super().on_key_press(symbol, modifiers)

    def on_mouse_press(self, x, y, button):
        """
        Creates a dot when the user clicks the mouse.
        If the dot intersects with the start button, then the game starts.
        """
        dot = Dot(x)
        if y == 'LEFT':
            intersection = Intersection(self.surround_start, dot)
            if intersection.width > 0 and intersection.height > 0:
                self.play(*[FadeOut(mob) for mob in [self.surround_start, self.start, self.pacman_text]])
                self.quit_interaction = True
