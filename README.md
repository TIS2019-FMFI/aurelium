Ak chce prevádzkovateľ exponátu zmeniť gestá, ich výpisy alebo dĺžky časov, je potrebné prepísať súbor confuguration.txt . 
Pri zmene je potrebné dodržať štruktúru, a to tak aby:
1.	Prvý riadok bolo číslo kamery
2.	Druhý riadok je číslo, ktoré určuje dĺžku pauzy v ms, po ktorej sa vyhodnotí gesto
3.	Tretí riadok je číslo, ktoré určuje dĺžku krátkeho úkonu v ms
4.	Štvrtý riadok je číslo, ktoré určuje dĺžku dlhého úkonu v ms
5.	Piaty riadok je číslo, ktoré určuje dĺžku zobrazenia výpisu po rozpoznaní gesta
6.	Všetky nasledujúce riadky definujú gestá
	
	o	 štruktúra riadku: “názov gesta““výpis“postupnosť úkonov
	
	o	 príklad: “pozdrav““Ahoj“Lrb (znamená že po postupnosti troch gest dlhé žmurknutie ľavým okom, krátke pravým a krátke oboma sa vypíše na obrazovke Ahoj)
	
	o	 Úkony, z ktorých sa gesto môže skladať:
		 L = dlhé zavretie ľavého oka
		 R = dlhé zavretie pravého oka
		 B = dlhé zavretie oboch očí súčasne
		 l = krátke zavretie ľavého oka
		 r = krátke zavretie pravého oka
		 b = krátke zavretie oboch očí súčasne

