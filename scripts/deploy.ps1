# PowerShell script to deploy Gradio Web App using az CLI
$BASE_NAME = "Chat-MVP-Gradio"
$LOCATION = "eastus3"
$APP_NAME = "as-${BASE_NAME}"
$RESOURCE_GROUP = "rg-${BASE_NAME}"
$PLAN_NAME = "asp-${BASE_NAME}"
$SKU = "P0V3"  # "B1", "F1"
# $SLOT = "staging"
$NUM_WORKERS = "2"
$RUNTIME = "PYTHON:3.13"
$MIN_TLS_CIPHER = "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"
$MIN_TLS_VERSION = "1.3"
$STARTUP_FILE = "bash ./startup.sh"  # /home/site/wwwroot/startup.sh"
$ZIP_7Z_PATH = "${env:ProgramFiles}\7-Zip\7z.exe"
$ZIP_TARGET_PATH = "../.azure/${BASE_NAME}.zip"
$ZIP_INCLUDES = @(
  "../src/", "../assets",
  "../requirements.txt", "../Makefile",
  "./startup.sh"
)
$AZ_COMMON_PARAMS = @(
  '--resource-group', $RESOURCE_GROUP
  '--output', 'none'
  '--only-show-errors'
)
$AZ_APP_PARAMS = $AZ_COMMON_PARAMS.Clone()
$AZ_APP_PARAMS += @( '--name', $APP_NAME )
$AZ_APP_AS_ONLY_PARAMS = @(
  '--https-only', 'true'
  '--basic-auth', 'Disabled'
)
$WH_PARAMS = @{ ForegroundColor = "Yellow" }

Write-Host "Zipping '${ZIP_INCLUDES}' to '${ZIP_TARGET_PATH}' ..." @WH_PARAMS
Remove-Item `
  -Path $ZIP_TARGET_PATH `
  -EA SilentlyContinue
# Using 7x.exe, Compress-Archive "\" but Linux demands "/"
Start-Process `
  -FilePath $ZIP_7Z_PATH `
  -ArgumentList "a -tzip ${ZIP_TARGET_PATH} ${ZIP_INCLUDES}" `
  -Wait -EA Stop

Write-Host "rg create ..." @WH_PARAMS
az group create @AZ_COMMON_PARAMS `
  --location $LOCATION

Write-Host "asp create ..." @WH_PARAMS
az appservice plan create @AZ_COMMON_PARAMS `
  --name $PLAN_NAME `
  --location $LOCATION `
  --number-of-workers $NUM_WORKERS `
  --sku $SKU `
  --is-linux

Write-Host "as create ..." @WH_PARAMS
az webapp create @AZ_APP_PARAMS `
  --plan $PLAN_NAME `
  --runtime $RUNTIME

if ($SLOT -and $SLOT -is [string]) {
  $AZ_APP_PARAMS += @('--slot', $SLOT)
  $slot_msg = "slot '${SLOT}' "
  Write-Host "as create ${slot_msg}..." @WH_PARAMS
  az webapp deployment slot create $AZ_APP_PARAMS
  az webapp update $AZ_APP_PARAMS `
    $AZ_APP_AS_ONLY_PARAMS
}

Write-Host "as set ..." @WH_PARAMS
az webapp config set @AZ_APP_PARAMS `
  --startup-file $STARTUP_FILE `
  --min-tls-cipher-suite $MIN_TLS_CIPHER `
  --min-tls-version $MIN_TLS_VERSION `
  --number-of-workers $NUM_WORKERS `
  --ftps-state FtpsOnly `
  --http20-enabled true `
  --remote-debugging-enabled false `
  --always-on false `
  --auto-heal-enabled true

# TODO
# authentification
# az webapp auth set $AZ_APP_PARAMS `
#  --enabled true --action LoginWithAzureActiveDirectory

# Property Available options: [
#   'additionalProperties', 'availabilityState', 'clientAffinityEnabled', 'clientCertEnabled',
#   'clientCertExclusionPaths', 'clientCertMode', 'cloningInfo', 'containerSize',
#   'customDomainVerificationId', 'dailyMemoryTimeQuota', 'daprConfig', 'defaultHostName',
#   'enabled', 'enabledHostNames', 'endToEndEncryptionEnabled', 'extendedLocation', 'hostNameSslStates',
#   'hostNames', 'hostNamesDisabled', 'hostingEnvironmentProfile', 'httpsOnly', 'hyperV', 'id',
#   'identity', 'inProgressOperationId', 'isDefaultContainer', 'isXenon', 'keyVaultReferenceIdentity',
#   'kind', 'lastModifiedTimeUtc', 'location', 'managedEnvironmentId', 'maxNumberOfWorkers', 'name',
#   'outboundIpAddresses', 'possibleOutboundIpAddresses', 'publicNetworkAccess', 'redundancyMode',
#   'repositorySiteName', 'reserved', 'resourceConfig', 'resourceGroup', 'scmSiteAlsoStopped',
#   'serverFarmId', 'siteConfig', 'slotSwapStatus', 'state', 'storageAccountRequired', 'suspendedTill',
#   'tags', 'targetSwapSlot', 'trafficManagerHostNames', 'type', 'usageState', 'virtualNetworkSubnetId',
#   'vnetContentShareEnabled', 'vnetImagePullEnabled', 'vnetRouteAllEnabled', 'workloadProfileName
# ']
# FIXME clientCertMode=Optional does not get set
# az webapp update @AZ_APP_PARAMS `
#   --set clientCertMode=Optional

# $app_res_id = $(az webapp show -r $RESOURCE_GROUP -n $APP_NAME --query id -o tsv)
# az resource update `
#   --ids $app_res_id `
#   --set properties.clientCertMode=Optional `
#   --only-show-errors

# az webapp config appsettings set @AZ_APP_PARAMS `
#   --settings SCM_DO_BUILD_DURING_DEPLOYMENT=false PORT=8000

# This command has been deprecated and will be removed in a future release.
# Use 'az webapp deploy' instead.
# az webapp deployment source config-zip @AZ_APP_PARAMS `
#   --src $ZIP_PATH

# create as slot
# az webapp deployment slot create @AZ_APP_PARAMS `
#   --slot $SLOT

Write-Host @WH_PARAMS "as deploy ..."
$as_deploy = $(
  az webapp deploy @AZ_APP_PARAMS `
    --src-path $ZIP_TARGET_PATH `
    --type zip `
    --restart true `
    --timeout 30000 `
    2>&1
    # --slot $SLOT
    # --async false
)

# az webapp config show `
#   --resource-group rg-gradio-webapp `
#   --name as-gradio-webapp `
#   --output json

az webapp log tail @AZ_APP_PARAMS

if ($as_deploy) {
  Write-Host "Error while deploying: ${as_deploy}" -ForegroundColor Red
}
else {
  Write-Host "App URL: https://${APP_NAME}.azurewebsites.net" @WH_PARAMS
}
