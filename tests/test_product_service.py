"""
Pruebas para ProductService

Este archivo contiene 8 pruebas principales para el servicio de productos/inventario.
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from app.services.inventory_service import ProductService
from app.schemas.inventory import ProductCreate, ProductUpdate, InventoryMovementCreate
from app.db.models import StockStatusEnum


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_create_product_success():
    """
    ID: PROD-001
    Nombre: Crear producto exitosamente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    mock_product = MagicMock()
    mock_product.id = str(uuid4())
    mock_product.name = "Proteína Whey"
    mock_product.description = "Proteína en polvo"
    mock_product.price = Decimal('80000.00')
    mock_product.available_quantity = Decimal('50')
    mock_product.capacity_value = Decimal('50')
    mock_product.unit_type = "unit"
    mock_product.currency = "COP"
    mock_product.photo_url = None
    mock_product.min_stock = Decimal('10')
    mock_product.max_stock = Decimal('100')
    mock_product.stock_status = StockStatusEnum.NORMAL
    mock_product.is_active = True
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_repo_instance.create.return_value = mock_product
        
        service = ProductService(mock_db)
        product_data = ProductCreate(
            name="Proteína Whey",
            description="Proteína en polvo",
            price=Decimal('80000.00'),
            capacity_value=Decimal('50'),
            unit_type="unit",
            currency="COP",
            min_stock=Decimal('10'),
            max_stock=Decimal('100')
        )
        
        result = service.create_product(product_data)
    
    assert result is not None
    assert result.name == "Proteína Whey"
    assert result.price == Decimal('80000.00')


def test_get_product_by_id():
    """
    ID: PROD-002
    Nombre: Obtener producto por ID
    """
    mock_db = MagicMock()
    product_id = str(uuid4())
    
    mock_product = MagicMock()
    mock_product.id = product_id
    mock_product.name = "Proteína Whey"
    mock_product.description = "Descripción"
    mock_product.price = Decimal('80000.00')
    mock_product.capacity_value = Decimal('50')
    mock_product.unit_type = "unit"
    mock_product.currency = "COP"
    mock_product.photo_url = None
    mock_product.available_quantity = Decimal('50')
    mock_product.min_stock = Decimal('10')
    mock_product.max_stock = Decimal('100')
    mock_product.stock_status = StockStatusEnum.NORMAL
    mock_product.is_active = True
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_repo_instance.get_by_id.return_value = mock_product
        
        service = ProductService(mock_db)
        result = service.get_product(product_id)
    
    assert result is not None
    assert result.id == product_id


def test_update_stock_add():
    """
    ID: PROD-003
    Nombre: Actualizar stock agregando cantidad usando add_stock
    """
    mock_db = MagicMock()
    product_id = str(uuid4())
    
    mock_product = MagicMock()
    mock_product.id = product_id
    mock_product.name = "Producto Test"
    mock_product.description = "Descripción"
    mock_product.capacity_value = Decimal('50')
    mock_product.unit_type = "unit"
    mock_product.price = Decimal('10000')
    mock_product.currency = "COP"
    mock_product.photo_url = None
    mock_product.available_quantity = Decimal('50')
    mock_product.min_stock = Decimal('10')
    mock_product.max_stock = Decimal('100')
    mock_product.stock_status = StockStatusEnum.NORMAL
    mock_product.is_active = True
    mock_product.created_at = datetime.now()
    mock_product.updated_at = datetime.now()
    
    updated_product = MagicMock()
    updated_product.id = product_id
    updated_product.name = "Producto Test"
    updated_product.description = "Descripción"
    updated_product.capacity_value = Decimal('70')
    updated_product.unit_type = "unit"
    updated_product.price = Decimal('10000')
    updated_product.currency = "COP"
    updated_product.photo_url = None
    updated_product.available_quantity = Decimal('70')
    updated_product.min_stock = Decimal('10')
    updated_product.max_stock = Decimal('100')
    updated_product.stock_status = StockStatusEnum.NORMAL
    updated_product.is_active = True
    updated_product.created_at = datetime.now()
    updated_product.updated_at = datetime.now()
    
    mock_movement = MagicMock()
    mock_movement.id = uuid4()
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        # El servicio llama get_by_id dos veces: al inicio y al final
        # Primera llamada retorna mock_product, segunda retorna updated_product
        mock_repo_instance.get_by_id.side_effect = [mock_product, updated_product]
        mock_repo_instance.update.return_value = updated_product
        
        with patch('app.services.inventory_service.MovementService') as mock_movement_service:
            mock_movement_instance = MagicMock()
            mock_movement_service.return_value = mock_movement_instance
            mock_movement_instance.create_movement.return_value = mock_movement
            
            service = ProductService(mock_db)
            # Usar add_stock en lugar de update_stock
            result_product, result_movement = service.add_stock(product_id, Decimal('20'))
    
    assert result_product is not None


def test_update_stock_subtract():
    """
    ID: PROD-004
    Nombre: Actualizar stock restando cantidad usando remove_stock
    """
    mock_db = MagicMock()
    product_id = str(uuid4())
    
    mock_product = MagicMock()
    mock_product.id = product_id
    mock_product.name = "Producto Test"
    mock_product.description = "Descripción"
    mock_product.capacity_value = Decimal('50')
    mock_product.unit_type = "unit"
    mock_product.price = Decimal('10000')
    mock_product.currency = "COP"
    mock_product.photo_url = None
    mock_product.available_quantity = Decimal('50')
    mock_product.min_stock = Decimal('10')
    mock_product.max_stock = Decimal('100')
    mock_product.stock_status = StockStatusEnum.NORMAL
    mock_product.is_active = True
    mock_product.created_at = datetime.now()
    mock_product.updated_at = datetime.now()
    
    updated_product = MagicMock()
    updated_product.id = product_id
    updated_product.name = "Producto Test"
    updated_product.description = "Descripción"
    updated_product.capacity_value = Decimal('30')
    updated_product.unit_type = "unit"
    updated_product.price = Decimal('10000')
    updated_product.currency = "COP"
    updated_product.photo_url = None
    updated_product.available_quantity = Decimal('30')
    updated_product.min_stock = Decimal('10')
    updated_product.max_stock = Decimal('100')
    updated_product.stock_status = StockStatusEnum.NORMAL
    updated_product.is_active = True
    updated_product.created_at = datetime.now()
    updated_product.updated_at = datetime.now()
    
    mock_movement = MagicMock()
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        # El servicio llama get_by_id dos veces: al inicio y al final
        # Primera llamada retorna mock_product, segunda retorna updated_product
        mock_repo_instance.get_by_id.side_effect = [mock_product, updated_product]
        mock_repo_instance.update.return_value = updated_product
        
        with patch('app.services.inventory_service.MovementService') as mock_movement_service:
            mock_movement_instance = MagicMock()
            mock_movement_service.return_value = mock_movement_instance
            mock_movement_instance.create_movement.return_value = mock_movement
            
            service = ProductService(mock_db)
            # Usar remove_stock en lugar de update_stock
            result_product, result_movement = service.remove_stock(product_id, Decimal('20'))
    
    assert result_product is not None


def test_get_all_products():
    """
    ID: PROD-005
    Nombre: Obtener todos los productos con paginación
    """
    mock_db = MagicMock()
    
    mock_product1 = MagicMock()
    mock_product1.id = str(uuid4())
    mock_product1.name = "Producto 1"
    mock_product1.description = "Desc 1"
    mock_product1.price = Decimal('10000')
    mock_product1.capacity_value = Decimal('10')
    mock_product1.unit_type = "unit"
    mock_product1.currency = "COP"
    mock_product1.photo_url = None
    mock_product1.available_quantity = Decimal('10')
    mock_product1.min_stock = Decimal('5')
    mock_product1.max_stock = Decimal('20')
    mock_product1.stock_status = StockStatusEnum.NORMAL
    mock_product1.is_active = True
    
    mock_product2 = MagicMock()
    mock_product2.id = str(uuid4())
    mock_product2.name = "Producto 2"
    mock_product2.description = "Desc 2"
    mock_product2.price = Decimal('20000')
    mock_product2.capacity_value = Decimal('20')
    mock_product2.unit_type = "unit"
    mock_product2.currency = "COP"
    mock_product2.photo_url = None
    mock_product2.available_quantity = Decimal('20')
    mock_product2.min_stock = Decimal('10')
    mock_product2.max_stock = Decimal('40')
    mock_product2.stock_status = StockStatusEnum.NORMAL
    mock_product2.is_active = True
    
    mock_products = [mock_product1, mock_product2]
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_repo_instance.get_all.return_value = mock_products
        mock_repo_instance.get_count.return_value = 2
        
        service = ProductService(mock_db)
        products, total = service.get_all_products(skip=0, limit=10, active_only=True)
    
    assert len(products) == 2
    assert total == 2


def test_get_low_stock_products():
    """
    ID: PROD-006
    Nombre: Obtener productos con stock bajo usando get_low_stock_alerts
    """
    mock_db = MagicMock()
    
    mock_product = MagicMock()
    mock_product.id = str(uuid4())
    mock_product.name = "Producto Bajo Stock"
    mock_product.description = "Descripción"
    mock_product.capacity_value = Decimal('5')
    mock_product.unit_type = "unit"
    mock_product.price = Decimal('10000')
    mock_product.currency = "COP"
    mock_product.photo_url = None
    mock_product.available_quantity = Decimal('5')
    mock_product.min_stock = Decimal('10')
    mock_product.max_stock = Decimal('20')
    mock_product.stock_status = StockStatusEnum.LOW_STOCK
    mock_product.is_active = True
    mock_product.created_at = datetime.now()
    mock_product.updated_at = datetime.now()
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_repo_instance.get_low_stock_products.return_value = [mock_product]
        
        service = ProductService(mock_db)
        result = service.get_low_stock_alerts()
    
    assert len(result) == 1


def test_update_product():
    """
    ID: PROD-007
    Nombre: Actualizar información de producto
    """
    mock_db = MagicMock()
    product_id = str(uuid4())
    
    mock_product = MagicMock()
    mock_product.id = product_id
    mock_product.name = "Proteína Whey"
    mock_product.price = Decimal('80000.00')
    mock_product.min_stock = Decimal('10')
    mock_product.max_stock = Decimal('100')
    
    updated_product = MagicMock()
    updated_product.id = product_id
    updated_product.name = "Proteína Whey Actualizada"
    updated_product.description = "Descripción"
    updated_product.capacity_value = Decimal('50')
    updated_product.unit_type = "unit"
    updated_product.price = Decimal('85000.00')
    updated_product.currency = "COP"
    updated_product.photo_url = None
    updated_product.available_quantity = Decimal('50')
    updated_product.min_stock = Decimal('10')
    updated_product.max_stock = Decimal('100')
    updated_product.stock_status = StockStatusEnum.NORMAL
    updated_product.is_active = True
    updated_product.created_at = datetime.now()
    updated_product.updated_at = datetime.now()
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_repo_instance.get_by_id.return_value = mock_product
        mock_repo_instance.update.return_value = updated_product
        
        service = ProductService(mock_db)
        product_update = ProductUpdate(
            name="Proteína Whey Actualizada",
            price=Decimal('85000.00')
        )
        
        result = service.update_product(product_id, product_update)
    
    assert result is not None
    assert result.name == "Proteína Whey Actualizada"


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_update_stock_insufficient():
    """
    ID: PROD-008
    Nombre: Error al restar stock insuficiente usando remove_stock
    """
    mock_db = MagicMock()
    product_id = str(uuid4())
    
    mock_product = MagicMock()
    mock_product.id = product_id
    mock_product.available_quantity = Decimal('10')  # Solo hay 10 unidades
    
    with patch('app.services.inventory_service.ProductRepository') as mock_repo_class:
        mock_repo_instance = MagicMock()
        mock_repo_class.return_value = mock_repo_instance
        mock_repo_instance.get_by_id.return_value = mock_product
        
        service = ProductService(mock_db)
        
        with pytest.raises(ValueError) as exc_info:
            service.remove_stock(product_id, Decimal('20'))  # Intentar restar 20
        
        assert "insufficient" in str(exc_info.value).lower() or "stock" in str(exc_info.value).lower()

