provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

# --- Lab Foundation (Azure) ---

resource "azurerm_resource_group" "lab" {
  name     = "rg-${var.project_name}-foundation-${var.environment}"
  location = var.location
}

# --- Event Hubs Namespace (Azure) ---

resource "azurerm_eventhub_namespace" "lab" {
  name                = "evhns-${var.project_name}-${var.environment}"
  location            = azurerm_resource_group.lab.location
  resource_group_name = azurerm_resource_group.lab.name
  sku                 = "Standard"
  capacity            = 2
}

# --- Managed Streaming for Kafka (AWS MSK) ---

resource "aws_msk_cluster" "lab" {
  cluster_name           = "msk-${var.project_name}-${var.environment}"
  kafka_version          = "3.2.0"
  number_of_broker_nodes = 3

  broker_node_group_info {
    instance_type = "kafka.m5.large"
    client_subnets = var.aws_subnets
    security_groups = [var.aws_security_group]
  }
}

# --- Lab Control Plane (AKS) ---

resource "azurerm_kubernetes_cluster" "lab_k8s" {
  name                = "aks-${var.project_name}-control-plane-${var.environment}"
  location            = azurerm_resource_group.lab.location
  resource_group_name = azurerm_resource_group.lab.name
  dns_prefix          = "eda-lab-k8s"

  default_node_pool {
    name       = "labpool"
    node_count = 3
    vm_size    = "Standard_D4s_v3"
  }

  identity {
    type = "SystemAssigned"
  }
}

# --- Institutional Pattern Store (Postgres) ---

resource "azurerm_postgresql_flexible_server" "lab" {
  name                   = "psql-${var.project_name}-metadata-${var.environment}"
  resource_group_name    = azurerm_resource_group.lab.name
  location               = azurerm_resource_group.lab.location
  version                = "13"
  administrator_login    = "labadmin"
  administrator_password = var.db_password
  storage_mb             = 32768
  sku_name               = "GP_Standard_D2ds_v4"
}

# --- Lab Secrets & Certificates ---

resource "azurerm_key_vault" "lab" {
  name                        = "kv-eda-lab-${var.environment}"
  location                    = azurerm_resource_group.lab.location
  resource_group_name         = azurerm_resource_group.lab.name
  enabled_for_disk_encryption = true
  tenant_id                   = var.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"
}
