# pylint: skip-file
"""Fixtures for tests."""

import pytest
import pandas as pd


@pytest.fixture
def sample_incident_xml_wrong_line():
    """An incident example for an incident not on Paddington/Bristol line."""

    return """
    <Incidents xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:com="http://nationalrail.co.uk/xml/common"
    xmlns="http://nationalrail.co.uk/xml/incident"
    xsi:schemaLocation="http://internal.nationalrail.co.uk/xml/XsdSchemas/External/Version5.0/nre-incident-v5-0.xsd">
    <PtIncident>
    <CreationTime>2025-03-17T12:10:12.447Z</CreationTime>
    <ChangeHistory>
    <com:ChangedBy>NRE CMS Editor</com:ChangedBy>
    <com:LastChangedDate>2025-06-02T08:28:13.743Z</com:LastChangedDate>
    </ChangeHistory>
    <IncidentNumber>DA3DF5FDF4074F90BE871AAB6F0B8D1F</IncidentNumber>
    <Version>20250602082813</Version>
    <ValidityPeriod>
    <com:StartTime>2025-06-09T00:00:00.000+01:00</com:StartTime>
    <com:EndTime>2025-06-13T23:59:00.000+01:00</com:EndTime>
    </ValidityPeriod>
    <Planned>true</Planned>
    <Summary>
    <![CDATA[ CANCELLED: Engineering work between Exeter St Davids and Exmouth from Monday 9 to Friday 13 June ]]>
    </Summary>
    <Description>
    <![CDATA[ <p>The evening engineering work scheduled to take place between Exeter St Davids and Exmouth on Monday to Thursday nights has been cancelled</p> ]]>
    </Description>
    <InfoLinks>
    <InfoLink>
    <Uri>https://www.nationalrail.co.uk/engineering-works/23-40-exd-exm-20250609/</Uri>
    <Label>Incident detail page</Label>
    </InfoLink>
    </InfoLinks>
    <Affects>
    <Operators>
    <AffectedOperator>
    <OperatorRef>GW</OperatorRef>
    <OperatorName>Great Western Railway</OperatorName>
    </AffectedOperator>
    </Operators>
    <RoutesAffected>
    <![CDATA[ <p>from Exeter St Davids to Exmouth</p> ]]>
    </RoutesAffected>
    </Affects>
    <IncidentPriority>2</IncidentPriority>
    </PtIncident>
    </Incidents>
    """


@pytest.fixture
def sample_incident_xml_right_line():
    """An incident example for an incident which is on Paddington/Bristol line."""

    return """
    <Incidents xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:com="http://nationalrail.co.uk/xml/common"
    xmlns="http://nationalrail.co.uk/xml/incident"
    xsi:schemaLocation="http://internal.nationalrail.co.uk/xml/XsdSchemas/External/Version5.0/nre-incident-v5-0.xsd">
    <PtIncident>
    <CreationTime>2025-03-17T12:10:12.447Z</CreationTime>
    <ChangeHistory>
    <com:ChangedBy>NRE CMS Editor</com:ChangedBy>
    <com:LastChangedDate>2025-06-02T08:28:13.743Z</com:LastChangedDate>
    </ChangeHistory>
    <IncidentNumber>DA3DF5FDF4074F90BE871AAB6F0B8D1F</IncidentNumber>
    <Version>20250602082813</Version>
    <ValidityPeriod>
    <com:StartTime>2025-06-09T00:00:00.000+01:00</com:StartTime>
    <com:EndTime>2025-06-13T23:59:00.000+01:00</com:EndTime>
    </ValidityPeriod>
    <Planned>true</Planned>
    <Summary>
    <![CDATA[ CANCELLED: Engineering work between Exeter St Davids and Exmouth from Monday 9 to Friday 13 June ]]>
    </Summary>
    <Description>
    <![CDATA[ <p>The evening engineering work scheduled to take place between Exeter St Davids and Exmouth on Monday to Thursday nights has been cancelled</p> ]]>
    </Description>
    <InfoLinks>
    <InfoLink>
    <Uri>https://www.nationalrail.co.uk/engineering-works/23-40-exd-exm-20250609/</Uri>
    <Label>Incident detail page</Label>
    </InfoLink>
    </InfoLinks>
    <Affects>
    <Operators>
    <AffectedOperator>
    <OperatorRef>GW</OperatorRef>
    <OperatorName>Great Western Railway</OperatorName>
    </AffectedOperator>
    </Operators>
    <RoutesAffected>
    <![CDATA[ <p>between London Paddington and Bristol Temple Meads</p> ]]>
    </RoutesAffected>
    </Affects>
    <IncidentPriority>2</IncidentPriority>
    </PtIncident>
    </Incidents>
    """


@pytest.fixture
def sample_extracted_data():
    """A sample DataFrame like what extract() would return."""

    return pd.DataFrame([
        {
            "start_time": "2025-06-09T00:00:00.000+01:00",
            "end_time": "2025-06-13T23:59:00.000+01:00",
            "description": "<p>The evening engineering work scheduled to take place between Exeter St Davids and Exmouth on Monday to Thursday nights has been cancelled</p>",
            "incident_number": "001",
            "version_number": "20250602082813",
            "is_planned": "true",
            "info_link": "https://www.nationalrail.co.uk/engineering-works/23-40-exd-exm-20250609/",
            "summary": "CANCELLED: Engineering work between Exeter St Davids and Exmouth from Monday 9 to Friday 13 June",
            "routes_affected": "<p>from Exeter St Davids to Exmouth</p>"
        },
        {
            "start_time": "2025-06-09T00:00:00.000+01:00",
            "end_time": "2025-06-13T23:59:00.000+01:00",
            "description": "<p>The evening engineering work scheduled to take place between Exeter St Davids and Exmouth on Monday to Thursday nights has been cancelled</p>",
            "incident_number": "002",
            "version_number": "20250602082813",
            "is_planned": "true",
            "info_link": "https://www.nationalrail.co.uk/engineering-works/23-40-exd-exm-20250609/",
            "summary": "CANCELLED: Engineering work between Exeter St Davids and Exmouth from Monday 9 to Friday 13 June",
            "routes_affected": "<p>between London Paddington and Bristol Temple Meads</p>"
        }
    ])
