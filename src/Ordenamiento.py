from Util.BibFileUtil import BibFileUtil

class GnomeSort:

    def comparar_entradas(a, b):
        # Comparar primero por el valor de orden (campo seleccionado)
        comparacion_valor_orden = (a.valor_orden > b.valor_orden) - (a.valor_orden < b.valor_orden)
        if comparacion_valor_orden != 0:
            return comparacion_valor_orden
        # Si los valores de orden son iguales, comparar por la clave
        return (a.clave > b.clave) - (a.clave < b.clave)
    
    def gnome_sort(arr):
        index = 0
        n = len(arr)
        
        while index < n:
            if index == 0:
                index += 1
            elif GnomeSort.comparar_entradas(arr[index], arr[index - 1]) >= 0:
                index += 1
            else:
                # Intercambiar elementos
                arr[index], arr[index - 1] = arr[index - 1], arr[index]
                index -= 1
        return