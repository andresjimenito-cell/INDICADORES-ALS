"""
core/filters.py
===============
Filtros centralizados y optimizados para el tablero ALS.
Elimina duplicación de código y mejora rendimiento con operaciones vectorizadas.
"""

import pandas as pd
from typing import Optional, Set


# ── CONSTANTES OPTIMIZADAS (frozenset para búsqueda O(1)) ─────────────────────

EXCLUIDOS_ENTREGADOS = frozenset({
    'ENTREGAD', 'ENTREGADO', 'ENTREGADOS', 'ENTREGADA', 'ENTREGADAS'
})

EXCLUIDOS_FLUJO_NATURAL = frozenset({
    'FN', 'FLUJO NATURAL', 'FLUJO_NATURAL', 'F.N.', 'FLUJO NAT', 
    'F/N', 'FLUJO-NATURAL', 'NATURAL', 'FLOWING'
})

EXCLUIDOS_BLOQUES_CAMPOS = frozenset({
    'CANAGUARO', 'ENTRERIOS', 'ENTRE RIOS', 'ENTRE RÍOS', 'ENTRE_RIOS',
    'MAPACHE', 'PERICO', 'PERICO (88)', 'MAPACHE PERICO', 'MAPACHE - PERICO',
    'MAPACHE/PERICO', 'MAPACHE-PERICO', 'CORCEL NE', 'CORCEL_NE', 'CORCEL-NE', 
    'CORCEL N3', 'CORCEL_N3', 'CORCEL-N3', 'RIO META', 'RIO_META', 'RÍO META', 
    'RÍO_META', 'EL DIFICIL', 'EL DIFICIL NE', 'DIFICIL', 'EL DIFÍCIL', 
    'EL DIFÍCIL NE', 'TODOS'
})

COLUMNAS_TEXTO_RELEVANTES = frozenset({
    'FECHA_PULL', 'FECHA_FALLA', 'ESTADO', 'COMENTARIOS', 'POZO',
    'RAZON_DE_PULL', 'RAZON ESPECIFICA PULL', 'OBSERVACIONES'
})

COLUMNAS_ALS_RELEVANTES = frozenset({
    'ALS', 'SISTEMA ALS', 'SISTEMA_ALS', 'METODO', 'METODO DE LEVANTAMIENTO',
    'TIPO_SISTEMA', 'EQUIPO'
})

COLUMNAS_UBICACION = frozenset({
    'ACTIVO', 'BLOQUE', 'CAMPO', 'AREA', 'REGION'
})


def limpiar_pozos_no_als(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Filtra pozos ENTREGADOS y FLUJO NATURAL de manera vectorizada y eficiente.
    
    Esta función centraliza la lógica de filtrado que estaba duplicada en:
    - INDICADORES.py
    - core/calculations.py  
    - data/data_loader.py
    - core/mtbf.py
    - core/run_life_efectivo.py
    
    Parámetros:
        df: DataFrame original con datos de pozos
        
    Retorna:
        DataFrame filtrado sin pozos ENTREGADOS ni FLUJO NATURAL
    """
    if df is None or df.empty:
        return df
    
    # Copia superficial para no modificar el original
    df = df.copy()
    
    # ── FILTRAR ENTREGADOS (una sola pasada vectorizada) ──────────────────────
    text_cols = [c for c in COLUMNAS_TEXTO_RELEVANTES if c in df.columns]
    if text_cols:
        # Crear máscara booleana vectorizada
        mask_entregados = pd.Series(False, index=df.index)
        
        for col in text_cols:
            col_mask = df[col].astype(str).str.upper().str.contains(
                '|'.join(EXCLUIDOS_ENTREGADOS), 
                na=False,
                regex=True
            )
            mask_entregados |= col_mask
        
        df = df[~mask_entregados]
    
    # ── FILTRAR FLUJO NATURAL (búsqueda con set precompilado) ─────────────────
    als_cols = [c for c in COLUMNAS_ALS_RELEVANTES if c in df.columns]
    if als_cols:
        mask_fn = pd.Series(False, index=df.index)
        
        for col in als_cols:
            col_mask = df[col].astype(str).str.strip().str.upper().isin(
                EXCLUIDOS_FLUJO_NATURAL
            )
            mask_fn |= col_mask
        
        df = df[~mask_fn]
    
    # ── EXCLUIR BLOQUES/CAMPOS NO RELEVANTES ───────────────────────────────────
    ubic_cols = [c for c in COLUMNAS_UBICACION if c in df.columns]
    if ubic_cols:
        mask_excluidos = pd.Series(False, index=df.index)
        
        for col in ubic_cols:
            col_mask = df[col].astype(str).str.upper().str.strip().isin(
                EXCLUIDOS_BLOQUES_CAMPOS
            )
            mask_excluidos |= col_mask
        
        df = df[~mask_excluidos]
    
    return df


def aplicar_filtros_globales(
    df: pd.DataFrame,
    activo: Optional[str] = None,
    bloque: Optional[str] = None,
    campo: Optional[str] = None,
    als: Optional[str] = None
) -> pd.DataFrame:
    """
    Aplica filtros globales de Activo, Bloque, Campo y Sistema ALS.
    
    Parámetros:
        df: DataFrame ya limpiado (sin ENTREGADOS/FN)
        activo: Valor del filtro de Activo (o None/TODOS para todos)
        bloque: Valor del filtro de Bloque (o None/TODOS para todos)
        campo: Valor del filtro de Campo (o None/TODOS para todos)
        als: Valor del filtro de Sistema ALS (o None/TODOS para todos)
        
    Retorna:
        DataFrame filtrado según los parámetros
    """
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    # Mapeo de columnas posibles
    col_activo = next((c for c in ['ACTIVO', 'BLOQUE', 'CAMPO'] if c in df.columns), None)
    col_bloque = next((c for c in ['BLOQUE', 'ACTIVO', 'CAMPO'] if c in df.columns), None)
    col_campo = next((c for c in ['CAMPO', 'ACTIVO', 'BLOQUE'] if c in df.columns), None)
    col_als = next((c for c in ['ALS', 'SISTEMA ALS', 'SISTEMA_ALS', 'METODO'] if c in df.columns), None)
    
    # Aplicar filtros solo si son específicos (no TODOS/None)
    if activo and activo != 'TODOS' and col_activo:
        df = df[df[col_activo].astype(str).str.upper().str.strip() == activo.upper()]
    
    if bloque and bloque != 'TODOS' and col_bloque:
        df = df[df[col_bloque].astype(str).str.upper().str.strip() == bloque.upper()]
    
    if campo and campo != 'TODOS' and col_campo:
        df = df[df[col_campo].astype(str).str.upper().str.strip() == campo.upper()]
    
    if als and als != 'TODOS' and col_als:
        df = df[df[col_als].astype(str).str.upper().str.strip() == als.upper()]
    
    return df


def obtener_opciones_filtro(df: pd.DataFrame, columna: str) -> list:
    """
    Obtiene opciones únicas para un filtro, excluyendo valores vacíos y no relevantes.
    
    Parámetros:
        df: DataFrame de origen
        columna: Nombre de la columna a analizar
        
    Retorna:
        Lista ordenada de valores únicos válidos, comenzando con 'TODOS'
    """
    if df is None or df.empty or columna not in df.columns:
        return ['TODOS']
    
    # Obtener valores únicos, limpiar y ordenar
    valores = (
        df[columna]
        .astype(str)
        .str.strip()
        .str.upper()
        .replace(['', 'NaN', 'NONE', 'NAN'], pd.NA)
        .dropna()
        .unique()
    )
    
    # Excluir valores no relevantes
    todos_excluidos = EXCLUIDOS_BLOQUES_CAMPOS | EXCLUIDOS_ENTREGADOS
    valores_validos = sorted([
        v for v in valores 
        if v not in todos_excluidos and len(v) > 0
    ])
    
    return ['TODOS'] + valores_validos
