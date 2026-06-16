async def generer_ticket_de_caisse(self, facture_id, **kwargs):
        """
        Génère un ticket thermique avec hauteur dynamique optimisée.
        Ancrage strict en haut du rouleau pour éliminer la marge supérieure fantôme.
        """
        font_reg, font_bold = self.charger_police_inter()
        
        # Récupération des données passées en kwargs
        date_heure = kwargs.get('date_heure', datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))
        self_user_name = kwargs.get('self_user_name', self.user_name if hasattr(self, 'user_name') else "Caissier")
        mode_paiement = kwargs.get('mode_paiement', "Espèces")
        total = kwargs.get('total', 0)
        encaisse = kwargs.get('encaisse', 0)
        rendu = kwargs.get('rendu', 0)
        items = kwargs.get('items', kwargs.get('articles', []))
        
        tenant_infos = kwargs.get('tenant_infos', {})
        if isinstance(tenant_infos, dict):
            nom_boutique = tenant_infos.get('nom_entreprise', kwargs.get('nom_boutique', 'Ma Boutique'))
            slogan = tenant_infos.get('slogan', kwargs.get('slogan', 'Vos actes parlent pour vous'))
            logo_url = tenant_infos.get('logo_url', kwargs.get('logo_url', None))
            adresse = tenant_infos.get('adresse', kwargs.get('adresse', ''))
            contact = tenant_infos.get('contact', kwargs.get('contact', ''))
        else:
            nom_boutique = getattr(tenant_infos, 'nom_entreprise', kwargs.get('nom_boutique', 'Ma Boutique'))
            slogan = getattr(tenant_infos, 'slogan', kwargs.get('slogan', 'Vos actes parlent pour vous'))
            logo_url = getattr(tenant_infos, 'logo_url', kwargs.get('logo_url', None))
            adresse = getattr(tenant_infos, 'adresse', kwargs.get('adresse', ''))
            contact = getattr(tenant_infos, 'contact', kwargs.get('contact', ''))

        # --- CALCUL GÉOMÉTRIQUE COMPACTÉ ---
        largeur_ticket = 80 * mm
        
        # Hauteurs minimales calculées au plus juste pour coller au texte
        H_LOGO = 15 if logo_url else 0
        H_ENTETE = 14  # Nom boutique + Slogan resserrés
        H_INFOS = 18   # Métadonnées du ticket
        H_FINANCE = 24 if str(mode_paiement).lower() in ["cash", "espèces", "especes"] else 14
        H_FOOTER = 26  # Messages, Adresse, Contact et lignes vides
        H_PAR_ARTICLE = 9.5  # Hauteur stricte par bloc article
        
        # Hauteur dynamique totale brute
        hauteur_ticket = (H_LOGO + H_ENTETE + H_INFOS + (len(items) * H_PAR_ARTICLE) + H_FINANCE + H_FOOTER) * mm
        
        chemin_pdf = "ticket_temp.pdf"
        c = canvas.Canvas(chemin_pdf, pagesize=(largeur_ticket, hauteur_ticket))
        
        # Verrouillage de la boîte de délimitation pour le pilote Epson
        c.setCropBox((0, 0, largeur_ticket, hauteur_ticket))
        
        # CORRECTION DE LA MARGE DU HAUT : On colle le curseur à seulement 3mm du bord physique supérieur
        y_cursor = hauteur_ticket - 3 * mm
        M_LEFT = 4 * mm
        M_RIGHT = largeur_ticket - 4 * mm
        C_CENTER = largeur_ticket / 2
        
        # --- SECTION EN-TÊTE & LOGO ---
        if logo_url:
            try:
                response = requests.get(logo_url, timeout=5)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    img = ImageReader(img_data)
                    c.drawImage(img, C_CENTER - (19 * mm), y_cursor - (13 * mm), width=38 * mm, height=13 * mm, preserveAspectRatio=True)
                    y_cursor -= 14 * mm
            except Exception as e:
                print(f"[REPORTLAB] Erreur logo : {e}")
                
        c.setFont(font_bold, 12)
        c.drawCentredString(C_CENTER, y_cursor, nom_boutique)
        y_cursor -= 4.5 * mm
        
        c.setFont(font_reg, 8.5)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawCentredString(C_CENTER, y_cursor, slogan)
        c.setFillColorRGB(0, 0, 0)
        y_cursor -= 5.5 * mm
        
        # --- SECTION INFOS DU TICKET ---
        c.setFont(font_reg, 8.5)
        c.drawString(M_LEFT, y_cursor, f"Ticket N° : {facture_id}")
        y_cursor -= 3.8 * mm
        c.drawString(M_LEFT, y_cursor, f"Date : {date_heure}")
        y_cursor -= 3.8 * mm
        c.drawString(M_LEFT, y_cursor, f"Caissier(e) : {self_user_name}")
        y_cursor -= 4.5 * mm
        
        # Ligne de séparation
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.5)
        c.setDash(2, 2)
        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 3.5 * mm
        
        # --- TABLEAU DES ARTICLES ---
        c.setDash()
        c.setFont(font_bold, 8.5)
        c.drawString(M_LEFT, y_cursor, "Désignation")
        c.drawRightString(M_RIGHT, y_cursor, "Total")
        y_cursor -= 2.8 * mm
        
        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 4 * mm
        
        # Parcours des articles
        for art in items:
            c.setFont(font_bold, 8.5)
            texte_art = art.get('designation', 'Article')
            if len(texte_art) > 26:
                texte_art = texte_art[:23] + "..."
            c.drawString(M_LEFT, y_cursor, texte_art)
            
            c.setFont(font_reg, 8.5)
            total_ligne = f"{int(art.get('total', 0)):,} FCFA"
            c.drawRightString(M_RIGHT, y_cursor, total_ligne)
            y_cursor -= 3.8 * mm
            
            c.setFillColorRGB(0.4, 0.4, 0.4)
            calcul_txt = f"{art.get('qte', 1)} x {int(art.get('prix', 0)):,}"
            c.drawString(M_LEFT, y_cursor, calcul_txt)
            c.setFillColorRGB(0, 0, 0)
            
            y_cursor -= 5.7 * mm
            
        # --- SECTION FINANCIÈRE ---
        c.setDash(2, 2)
        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 4 * mm
        c.setDash()
        
        c.setFont(font_bold, 11)
        c.drawString(M_LEFT, y_cursor, "TOTAL FACTURE :")
        c.drawRightString(M_RIGHT, y_cursor, f"{int(total):,} FCFA")
        y_cursor -= 5 * mm
        
        c.setFont(font_reg, 8.5)
        c.drawString(M_LEFT, y_cursor, "Mode de paiement :")
        c.drawRightString(M_RIGHT, y_cursor, mode_paiement)
        y_cursor -= 3.8 * mm
        
        if str(mode_paiement).lower() in ["cash", "espèces", "especes"]:
            c.drawString(M_LEFT, y_cursor, "Montant Encaissé :")
            c.drawRightString(M_RIGHT, y_cursor, f"{int(encaisse):,} FCFA")
            y_cursor -= 3.8 * mm
            
            c.drawString(M_LEFT, y_cursor, "Montant Rendu :")
            c.drawRightString(M_RIGHT, y_cursor, f"{int(rendu):,} FCFA")
            y_cursor -= 4.5 * mm
            
        # --- FOOTER ---
        c.setDash(2, 2)
        c.line(M_LEFT, y_cursor, M_RIGHT, y_cursor)
        y_cursor -= 4 * mm
        c.setDash()
        
        # 1. Message de confiance
        c.setFont(font_bold, 8.5)
        c.drawCentredString(C_CENTER, y_cursor, "Merci de votre confiance !")
        y_cursor -= 4 * mm
        
        # 2. Adresse
        if adresse:
            c.setFont(font_reg, 8)
            c.drawCentredString(C_CENTER, y_cursor, f"Adresse : {adresse}")
            y_cursor -= 3.8 * mm
            
        # 3. Contact
        if contact:
            c.setFont(font_reg, 8)
            c.drawCentredString(C_CENTER, y_cursor, f"Contact : {contact}")
            y_cursor -= 3.8 * mm
            
        # 4. Message de fin
        c.setFont(font_reg, 7.5)
        c.drawCentredString(C_CENTER, y_cursor, "*** À bientôt ***")
        
        # 5. ESPACE BLANC DE FIN DE TICKET
        # On descend le curseur pour laisser la place physique au massicot sans toucher le texte
        y_cursor -= 14 * mm 
        
        # Sécurité pour s'assurer que ReportLab alloue bien l'espace jusqu'en bas
        c.drawString(M_LEFT, y_cursor, "") 
        
        c.showPage()
        c.save()
        
        return chemin_pdf
    