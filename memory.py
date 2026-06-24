async def get_ca_kpis(self):
    try:
        params = {'select': "*"}
        kpi_ca = await supabase_request_async(
            access_token=self.access_token,
            tenant_id=self.tenant_id,
            table_name="v_kpi_chiffre_affaires",
            method="GET",
            params=params
        )
        print(f"DEBUG [kpi CA]: | type: {type(kpi_ca)} | valeur: {kpi_ca}")

        if isinstance(kpi_ca, list) and len(kpi_ca) > 0:
            ca_global = kpi_ca[0].get('ca_total', 0)
            self.ca_global.value = format_milliers_fr(ca_global)
            print(f"DEBUG [ca_global] | {ca_global}")

            ca_mois = kpi_ca[0].get('ca_mois_en_cours')
            ca_mois_passe = kpi_ca[0].get('ca_mois_dernier')
            progres_mois = ca_mois - ca_mois_passe
            percent_mois = 100 if ca_mois_passe == 0 else progres_mois * 100 / ca_mois_passe
            self.ca_mois.value = format_milliers_fr(ca_mois)
            print(f"DEBUG [ca_mois] | {ca_mois}")
            print(f"DEBUG [ca_mois_passe] | {ca_mois_passe}")
            print(f"DEBUG [percent_mois] | {percent_mois}")

            ca_jour = kpi_ca[0].get('ca_aujourdhui')
            ca_hier = kpi_ca[0].get('ca_hier')
            progres_jour = ca_jour - ca_hier
            percent_jour = 100 if ca_hier == 0 else progres_jour * 100 / ca_hier
            self.ca_jour.value = format_milliers_fr(ca_jour)
            print(f"DEBUG [ca_jour] | {ca_jour}")
            print(f"DEBUG [ca_hier] | {ca_hier}")
            print(f"DEBUG [percent_jour] | {percent_jour}")

            self.ca_stats.controls.clear()
            self.ca_stats.controls.extend([
                self.build_stat_item("CA global", "assets/icons/grey/dollar-sign.svg", self.ca_global, None),
                self.build_stat_item("CA mois en cours", "assets/icons/grey/badge-cent.svg", self.ca_mois,
                                     percent_mois),
                self.build_stat_item("CA aujourd'hui", "assets/icons/grey/badge-cent.svg", self.ca_jour, percent_jour),
            ])
            # self.cp.page.update()

    except Exception as e:
        print(f"[ERREUR KPI CA] : {e}")
