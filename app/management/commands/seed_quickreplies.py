from django.core.management.base import BaseCommand
from app.models import QuickReply


class Command(BaseCommand):
    help = 'Créer les quick replies pour le bot messenger'

    def handle(self, *args, **options):
        # Données des quick replies
        quick_replies_data = [ 
            {
                'title': 'À propos',
                'payload': 'ABOUT',
                'response_text': 'HOSODOKO-KO est une maison de production d\'œuvre d\'art à partir de recyclage des déchets.\n\n🎯 VISION: Être une référence de la gestion des déchets et dans l\'éducation et sensibilisation environnementales avec une approche participative et inclusive.\n\n🎨 MISSIONS:\n• Valoriser les déchets en œuvre d\'arts originaux et inspirants\n• Promouvoir l\'écoresponsabilité grâce à des approches ludiques\n• Fédérer un réseau d\'acteurs locaux\n• Diffuser les connaissances en gestion des déchets\n\n💎 VALEURS: Création et innovation, Durabilité, Intégrité et transparence, Éducation et partage\n\n📧 Contact: hosodokoko@gmail.com | ☎️ +261 34 20 801 09'
            },
            {
                'title': 'Savoir-faire',
                'payload': 'SKILLS',
                'response_text': '🎨 NOS EXPERTISES:\n• Valorisation, recyclage et réutilisation des déchets à des fins d\'œuvres d\'arts\n• Éducation environnementale et sensibilisation\n• Renforcement de capacité des communautés\n• Reboisement communautaire\n• Restauration écologique participative\n• Inventaire et suivis écologiques\n• Valorisation des ressources naturelles\n\nNous mettons l\'art au service de l\'environnement avec une approche participative et inclusive.'
            },
            {
                'title': 'Événements',
                'payload': 'EVENTS',
                'response_text': '🌱 NOS ÉVÉNEMENTS:\n• Ateliers de création d\'œuvres d\'art à partir de déchets recyclés\n• Sessions d\'éducation environnementale\n• Campagnes de sensibilisation à la protection de l\'environnement\n• Projets de reboisement communautaire\n• Formations en gestion des déchets\n• Expositions d\'art écologique\n\nContactez-nous pour participer à nos prochaines activités ! 📧 hosodokoko@gmail.com'
            },
            {
                'title': 'Challenges',
                'payload': 'CHALLENGES',
                'response_text': '🎯 NOS DÉFIS:\n• Transformer la perception des déchets en ressources créatives\n• Sensibiliser les communautés à l\'écoresponsabilité\n• Créer un réseau d\'acteurs locaux engagés\n• Développer des approches ludiques pour l\'éducation environnementale\n• Promouvoir une culture de responsabilité environnementale\n• Restaurer les écosystèmes dégradés\n\nEnsemble, construisons un avenir plus durable ! 🌍'
            },
            # {
            #     'title': 'Quizz',
            #     'payload': 'QUIZ',
            #     'response_text': 'Quel est le plat japonais traditionnel souvent servi lors des célébrations ?\n1. Sushi\n2. Ramen\n3. Mochi\n4. Tempura\nRépondez avec le numéro de votre choix !'
            # }
        ]

        # Créer ou mettre à jour les quick replies
        for qr_data in quick_replies_data:
            quick_reply, created = QuickReply.objects.get_or_create(
                payload=qr_data['payload'],
                defaults={
                    'title': qr_data['title'],
                    'response_text': qr_data['response_text']
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Quick reply "{quick_reply.title}" créé avec succès')
                )
            else:
                # Mettre à jour les champs si nécessaire
                updated = False
                if quick_reply.title != qr_data['title']:
                    quick_reply.title = qr_data['title']
                    updated = True
                if quick_reply.response_text != qr_data['response_text']:
                    quick_reply.response_text = qr_data['response_text']
                    updated = True
                
                if updated:
                    quick_reply.save()
                    self.stdout.write(
                        self.style.WARNING(f'Quick reply "{quick_reply.title}" mis à jour')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Quick reply "{quick_reply.title}" existe déjà')
                    )

        self.stdout.write(
            self.style.SUCCESS('Toutes les quick replies ont été traitées avec succès!')
        )
