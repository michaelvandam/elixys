package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.geom.Rectangle;
	
	// This data grid component is an extension of the Form class
	public class DataGrid extends Form
	{
		/***
		 * Construction
		 **/
		
		public function DataGrid(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Extract the header details
			if (xml.@headerfontface.length() > 0)
			{
				m_sHeaderFontFace = xml.@headerfontface[0];
			}
			if (xml.@headerfontsize.length() > 0)
			{
				m_nHeaderFontSize = parseInt(xml.@headerfontsize[0]);
			}
			if (xml.@headertextcolor.length() > 0)
			{
				m_nHeaderTextColor = Styling.AS3Color(xml.@headertextcolor[0]);
			}
			if (xml.@headerpressedcolor.length() > 0)
			{
				m_nHeaderPressedColor = Styling.AS3Color(xml.@headerpressedcolor[0]);
			}
			if (xml.@sortupskin.length() > 0)
			{
				m_sSortUpSkin = xml.@sortupskin[0];
			}
			if (xml.@sortdownskin.length() > 0)
			{
				m_sSortDownSkin = xml.@sortdownskin[0];
			}

			// Extract the body details
			if (xml.@bodyfontface.length() > 0)
			{
				m_sBodyFontFace = xml.@bodyfontface[0];
			}
			if (xml.@bodyfontsize.length() > 0)
			{
				m_nBodyFontSize = parseInt(xml.@bodyfontsize[0]);
			}
			if (xml.@bodytextcolor.length() > 0)
			{
				m_nBodyTextColor = Styling.AS3Color(xml.@bodytextcolor[0]);
			}
			if (xml.@visiblerowcount.length() > 0)
			{
				m_nVisibleRowCount = parseInt(xml.@visiblerowcount[0]);
			}
			if (xml.@rowselectedcolor.length() > 0)
			{
				m_nRowSelectedColor = Styling.AS3Color(xml.@rowselectedcolor[0]);
			}

			// Call the base constructor
			super(screen, DATAGRID, attributes);
			
			// Get references to our header and body
			m_pDataGridHeader = findViewById("datagrid_header") as DataGridHeader;
			m_pDataGridBody = findViewById("datagrid_body") as DataGridBody;
			
			// Pass parameters to the header and body
			m_pDataGridHeader.SetParameters(m_sHeaderFontFace, m_nHeaderFontSize, m_nHeaderTextColor, m_nHeaderPressedColor,
				m_sSortUpSkin, m_sSortDownSkin);
			m_pDataGridBody.SetParameters(m_sBodyFontFace, m_nBodyFontSize, m_nBodyTextColor, m_nVisibleRowCount, m_nRowSelectedColor);
		}
		
		/***
		 * Member functions
		 **/

		// Update the data grid
		public function UpdateDataGrid(pColumns:Array, pData:Array):void
		{
			// Update the header and body
			m_pDataGridHeader.UpdateHeader(pColumns);
			m_pDataGridBody.UpdateBody(pColumns, pData);
		}

		// Override the layout function to adjust the size
		public override function layout(attributes:Attributes):void
		{
			// Set our width and height to that of the container
			if (parent is Form)
			{
				attributes.width = (parent as Form).attributes.width;
				attributes.height = (parent as Form).attributes.height;
			}
			
			// Call the base constructor
			super.layout(attributes);
		}

		/***
		 * Member functions
		 **/
		
		// Datagrid XML
		protected static const DATAGRID:XML = 
			<columns gapH="0" widths="15,100%,15">
				<frame />
				<rows heights="8%,6,92%,14,15" gapV="0">
					<datagridheader id="datagrid_header" />
					<frame background={Styling.TEXT_GRAY4} />
					<frame background={Styling.TEXT_GRAY4} alignH="fill">
						<datagridbody id="datagrid_body" />
					</frame>
					<frame background={Styling.TEXT_GRAY4} />
				</rows>
			</columns>;

		// Header and body components
		protected var m_pDataGridHeader:DataGridHeader;
		protected var m_pDataGridBody:DataGridBody;
		
		// Header details
		protected var m_sHeaderFontFace:String = "";
		protected var m_nHeaderFontSize:uint = 0;
		protected var m_nHeaderTextColor:uint = 0;
		protected var m_nHeaderPressedColor:uint = 0;
		protected var m_sSortUpSkin:String = "";
		protected var m_sSortDownSkin:String = "";
		
		// Body details
		protected var m_sBodyFontFace:String = "";
		protected var m_nBodyFontSize:uint = 0;
		protected var m_nBodyTextColor:uint = 0;
		protected var m_nVisibleRowCount:uint = 0;
		protected var m_nRowSelectedColor:uint = 0;
		
		// Constants used by both the header and body
		public static var TEXT_INDENT:uint = 20;
	}
}
