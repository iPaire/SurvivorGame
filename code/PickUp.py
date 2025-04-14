import pygame

class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, image, effect):
        super().__init__()
        self.image = pygame.image.load(image).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.effect = effect  # Poate fi "health", "ammo", "weapon", "speed" etc.

    def apply_effect(self, player):
        """Aplică efectul asupra jucătorului."""
        if self.effect == "health":
            player.health = min(player.health + 20, player.max_health)
        elif self.effect == "ammo":
            player.ammo += 10
        elif self.effect == "speed":
            player.speed += 1
        elif self.effect == "weapon":
            player.change_weapon("shotgun")  # Exemplar, schimbă arma

        self.kill()  # Șterge obiectul după ce e ridicat
