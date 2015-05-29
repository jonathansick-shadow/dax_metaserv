ASCII Schema Structure
======================

A typical DBMS stores information about databases it maintains. The structure of such information is typically fixed, and additional custom information is hard to capture. To overcome this, our DDL loader recognizes special optional tags, which need to be placed in appropriate places inside comments.

Currently supported tags:
<ul>
  <li><b>&lt;descr&gt;</b>: the contents between &lt;descr&gt; and &lt;/descr&gt; will contain description (of a table or a column),
  <li><b>&lt;unit&gt;</b>: the contents between &lt;unit&gt; and &lt;/unit&gt; will contain definition of a unit,
  <li><b>&lt;ucd&gt;</b>: the contents between &lt;ucd&gt; and &lt;/ucd&gt; will contain ucd value.
</ul>

Multi-lines are allowed for &lt;descr&gt; Examples of a valid multi-line entries:

    -- <descr>This is a valid entry.
    -- </descr>

    -- <descr>This is a
    -- valid entry
    -- as well.</descr>

    -- <descr>
    -- So is this.
    -- </descr>

Lines are stitched together into a single line: new lines are turned into spaces, and extranous spaces are turned into a single space.

Table Description
-----------------

To add a table description, use &lt;descr&gt;&lt;/descr&gt; right after table name, before the opening bracket. Example:

    CREATE TABLE MyTable
       -- <descr>This is my table.</descr>
    (


Column Description, UCDs, units
-------------------------------

To add a column description, use &lt;descr&gt;&lt;/descr&gt;

To add a unit for a given column, use &lt;unit&gt;&lt;/unit&gt;

To add a Unified Content Descriptor (ucd) for a given column, use &lt;ucd&gt;&lt;/ucd&gt;
The UCDs should be defined according to: [The UCD1+ controlled vocabulary](http://www.ivoa.net/Documents/cover/UCDlist-20070402.html)

These values should appear right after the column definition, in any order. Example:

    ra DOUBLE NOT NULL,
        -- <descr>RA-coordinate of the center of this diaObject.</descr>
        -- <ucd>stat.error;pos.eq.ra</ucd>
        -- <unit>deg</unit>

Other Notes
-----------

Note that the parser interpreting the ASCII schema is relatively simple, and it is not fully bullet proof, e.g., don't expect some random combinations of tags to work. If you run into problems with a syntax that feels like "it should work", file a bug report and we will gladly fix it!
