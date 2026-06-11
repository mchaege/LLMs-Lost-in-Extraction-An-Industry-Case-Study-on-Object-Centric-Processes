from src.ai import OcelRelation, OcelAttribute, OcelEntity, OcelEvent, OcelObject


truth = OcelEntity(
    objs=[
        OcelObject(
            name="Document",
            description="",
            attributes=[
                OcelAttribute(
                    name="Document type", 
                    description=""
                ),
                OcelAttribute(
                    name="Document level", 
                    description=""
                ),
                OcelAttribute(
                    name="References", 
                    description=""
                ),
                OcelAttribute(
                    name="Applications", 
                    description=""
                ),
                OcelAttribute(
                    name="Area of validity", 
                    description=""
                ),
                OcelAttribute(
                    name="Relevant companies", 
                    description=""
                ),
                OcelAttribute(
                    name="Version", 
                    description=""
                ),
                OcelAttribute(
                    name="Reader", 
                    description=""
                ),
                OcelAttribute(
                    name="Author", 
                    description=""
                ),
                OcelAttribute(
                    name="Co-author", 
                    description=""
                ),
                OcelAttribute(
                    name="Reviewer", 
                    description=""
                ),
                OcelAttribute(
                    name="Releaser", 
                    description=""
                ),
                OcelAttribute(
                    name="Release status", 
                    description=""
                ),
                OcelAttribute(
                    name="Validity timeframe", 
                    description=""
                ),
                OcelAttribute(
                    name="Archive duration", 
                    description=""
                ),
                OcelAttribute(
                    name="Distribution list", 
                    description=""
                ),
                OcelAttribute(
                    name="Translation status",
                    description=""
                )
            ]
        ),
        OcelObject(
            name="Process",
            description="",
            attributes=[]
        ),
        OcelObject(
            name="Organizational unit",
            description="",
            attributes=[]
        ),
        OcelObject(
            name="Risk",
            description="",
            attributes=[]
        ),
        OcelObject(
            name="User group",
            description="",
            attributes=[]
        ),
        OcelObject(
            name="Additional information",
            description="",
            attributes=[]
        ),
        OcelObject(
            name="Equipment",
            description="",
            attributes=[]
        ),
        OcelObject(
            name="Attachment",
            description="",
            attributes=[
                OcelAttribute(
                    name="Version",
                    description=""
                ),
                OcelAttribute(
                    name="Release status",
                    description=""
                )
            ]
        ),
        OcelObject(
            name="Authorization",
            description="",
            attributes=[]
        ),
        OcelObject(
            name="User",
            description="",
            attributes=[
                OcelAttribute(
                    name="Role",
                    description=""
                )
            ]
        ),
        OcelObject(
            name="Change proposal",
            description="",
            attributes=[]
        ),
    ],
    evts=[
        OcelEvent(
            name="Create Document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Edit Document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Release Document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Distribute Document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Archive Document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Link Document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Add additional information",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Add equipment",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Release additional information",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Publish additional information",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Create additional information",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Modify additional information",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Delete additional information",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Create attachment",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Modify attachment",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Archive attachment",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Assign authorization",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Acknowledge document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Sign change proposal",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Create change proposal",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Review document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Reject review",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Reject release",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Revise document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Schedule change proposal for implementation",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Review for validity",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Reactivate document",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Request for validity extension",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Extend validity by releaser",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Extend validity by all workflow participants",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Invalidate document by releaser",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Invalidate document by all workflow participants",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Create and check AKS request",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Review AKS",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Approve AKS",
            description="",
            attributes=[]
        ),
        OcelEvent(
            name="Create request for reactivation",
            description="",
            attributes=[]
        )
    ],
    o2o=[
        OcelRelation(
            a="Document",
            b="Process",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="Organizational unit",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="Risk",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="User group",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="Additional information",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="Equipment",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="Authorization",
            description=""
        ),
        OcelRelation(
            a="Authorization",
            b="User group",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="User",
            description=""
        ),
        OcelRelation(
            a="User",
            b="User group",
            description=""
        ),
        OcelRelation(
            a="Document",
            b="Change proposal",
            description=""
        )
    ],
    o2e=[
        OcelRelation(
            a="Create Document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Edit Document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Release Document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Distribute Document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Archive Document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Link Document",
            b="Process",
            description=""
        ),
        OcelRelation(
            a="Link Document",
            b="Organizational unit",
            description=""
        ),
        OcelRelation(
            a="Link Document",
            b="Risk",
            description=""
        ),
        OcelRelation(
            a="Link Document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Add additional information",
            b="Additional information",
            description=""
        ),
        OcelRelation(
            a="Add equipment",
            b="Equipment",
            description=""
        ),
        OcelRelation(
            a="Add additional information",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Add Equipment",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Release additional information",
            b="Additional information",
            description=""
        ),
        OcelRelation(
            a="Publish additional information",
            b="Additional information",
            description=""
        ),
        OcelRelation(
            a="Create additional information",
            b="Additional information",
            description=""
        ),
        OcelRelation(
            a="Modify additional information",
            b="Additional information",
            description=""
        ),
        OcelRelation(
            a="Delete additional information",
            b="Additional information",
            description=""
        ),
        OcelRelation(
            a="Create attachment",
            b=" Attachment",
            description=""
        ),
        OcelRelation(
            a="Modify attachment",
            b="Attachment",
            description=""
        ),
        OcelRelation(
            a="Archive attachment",
            b="Attachment",
            description=""
        ),
        OcelRelation(
            a="Assign authorization",
            b="Authorization",
            description=""
        ),
        OcelRelation(
            a="Acknowledge document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Acknowledge document",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Sign document creation",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Sign document creation",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Create change proposal",
            b="Change proposal",
            description=""
        ),
        OcelRelation(
            a="Review document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Review document",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Release document",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Reject review",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Reject release",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Revise document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Schedule change proposal for implementation",
            b="Change proposal",
            description=""
        ),
        OcelRelation(
            a="Review for validity",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Reactivate document",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Request for validity extension",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Extend validity by releaser",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Extend validity by releaser",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Extend validity by all workflow participants",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Extend validity by all workflow participants",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Invalidate document by releaser",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Invalidate document by releaser",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Invalidate document by all workflow participants",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Invalidate document by all workflow participants",
            b="User",
            description=""
        ),
        OcelRelation(
            a="Create and check AKS request",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Review AKS",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Approve AKS",
            b="Document",
            description=""
        ),
        OcelRelation(
            a="Create request for reactivation",
            b="Document",
            description=""
        ),
    ]
)