from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.log import logger

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('umanot.site_various.txt') is None:
        return

    # Add additional setup code here

def addCatalogIndexes(context):
    """
    The last bit of code that runs as part of this setup profile.
    """
    site = context.getSite()
    catalog = getToolByName(site, 'portal_catalog')
    indexes = catalog.indexes()
    wanted = (
        ("getFeatured", "BooleanIndex"),
        ("getHomepage_featured", "BooleanIndex"),
        ("getFooter_featured", "BooleanIndex"),
    )

    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            catalog.addColumn(name)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)