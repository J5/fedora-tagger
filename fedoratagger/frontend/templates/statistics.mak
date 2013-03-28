<table class="statistics">
<tr><td>Total Packages</td><td>${str(summary['total_packages'])}</td></tr>
<tr><td>Total Unique Tags</td><td>${str(summary['total_unique_tags'])}</td></tr>
<tr><td>Packages Without Tags</td><td>${str(summary['no_tags'])}</td></tr>
<tr><td>Packages With Tags</td><td>${str(summary['with_tags'])}</td></tr>
<tr><td>Average Tags / Package</td><td>${str(summary['tags_per_package'])}</td></tr>
<tr><td>Tags / Package (that have at least one tag)</td>
<td>${str(summary['tags_per_package_no_zeroes'])}</td></tr>
</table>
