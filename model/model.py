from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

        self.dict_prezzi = {}

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori() # lista

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        for distributore in self._distributori:
            lista_prezzi = PrezzoDAO.get_prezzi(distributore.id)
            for giorno in lista_prezzi:
                if giorno.data.month == mese:
                    if distributore.id not in self.dict_prezzi:
                        self.dict_prezzi[distributore.id] = [giorno.prezzo_litro]
                    else:
                        self.dict_prezzi[distributore.id].append(giorno.prezzo_litro)
        lista_medie = []
        for distributore in self.dict_prezzi:
            media = sum(self.dict_prezzi[distributore]) / len(self.dict_prezzi[distributore])
            lista_medie.append((distributore, media))
        return lista_medie

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        self.__get_prezzi_prima_settimana_mese(mese)

        self.__sequenza_ottima, self.__costo_ottimo = self.__ricorsione([], 1, None, 0, self.__get_prezzi_prima_settimana_mese(mese))

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if ultimo_distributore == 1:
            altro_distributore = 2
        else:
            altro_distributore = 1

        if len(sequenza_parziale) == 7:
            return sequenza_parziale, costo_corrente
        elif len(sequenza_parziale) == 0:
            if prezzi_settimana[1][0] <= prezzi_settimana[2][0]:
                sequenza_parziale.append(1)
                costo_corrente += (prezzi_settimana[1][0]*100)
                ultimo_distributore = 1
            else:
                sequenza_parziale.append(2)
                costo_corrente += (prezzi_settimana[2][0]*100)
                ultimo_distributore = 2
            giorno = 0
            #print(sequenza_parziale)
            return self.__ricorsione(sequenza_parziale, giorno + 1, ultimo_distributore, costo_corrente,
                                     prezzi_settimana)
        else:
            '''print(f"DEBUG PREZZO SETTIMANA: {prezzi_settimana}")
            print(f"DEBUG PREZZO ULTIMO DISTRIBUTORE: {ultimo_distributore}, {prezzi_settimana[ultimo_distributore][giorno]*100}")
            print(f"DEBUG PREZZO ALTRO DISTRIBUTORE: {altro_distributore}, {prezzi_settimana[ultimo_distributore][giorno] * 100 +5}")'''
            if (prezzi_settimana[ultimo_distributore][giorno]*100) > (prezzi_settimana[altro_distributore][giorno]*100 + 5):
                ultimo_distributore = altro_distributore
                costo_corrente += 5
            sequenza_parziale.append(ultimo_distributore)
            costo_corrente += (prezzi_settimana[ultimo_distributore][giorno]*100)
            return self.__ricorsione(sequenza_parziale, giorno + 1, ultimo_distributore, costo_corrente,
                                         prezzi_settimana)



    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        dict_prezzi = {}
        for distributore in self._distributori:
            lista_prezzi = PrezzoDAO.get_prezzi(distributore.id)
            for giorno in lista_prezzi:
                if giorno.data.month == mese:
                    if distributore.id not in dict_prezzi:
                        dict_prezzi[distributore.id] = [giorno.prezzo_litro]
                    else:
                        dict_prezzi[distributore.id].append(giorno.prezzo_litro)

        dict_settimana = {}
        for distributore in dict_prezzi:
            dict_settimana[distributore] = dict_prezzi[distributore][0:7]

        return dict_settimana
