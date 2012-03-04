package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Column;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	
	// This data grid body component is an extension of the UIScrollVertical class
	public class DataGridBody extends UIScrollVertical
	{
		/***
		 * Construction
		 **/
		
		public function DataGridBody(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, DATAGRIDBODY, attributes);

			// Enable the mask
			scrollRect = new Rectangle(0, 0, attributes.width, attributes.height);
		}
		
		/***
		 * Member functions
		 **/

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

		// Override the hit searching function
		protected override function doSearchHit():void
		{
			// Convert from local to global coordinates
			var pLocalPoint:Point = new Point(_slider.mouseX, _slider.mouseY);
			var pGlobalPoint:Point = _slider.localToGlobal(pLocalPoint);

			// Check for a row click
			for (var nIndex:int = 0; nIndex < m_pHitAreasGlobal.length; ++nIndex)
			{
				if ((m_pHitAreasGlobal[nIndex] as Rectangle).contains(pGlobalPoint.x, pGlobalPoint.y))
				{
					// Set the selected row index and render
					m_nSelectedRow = nIndex;
					Render();
					break;
				}
			}
		}

		// Set data grid header parameters
		public function SetParameters(sFontFace:String, nFontSize:uint, nTextColor:uint, nVisibleRowCount:uint, nSelectedColor:uint):void
		{
			m_sFontFace = sFontFace;
			m_nFontSize = nFontSize;
			m_nTextColor = nTextColor;
			m_nVisibleRowCount = nVisibleRowCount;
			m_nSelectedColor = nSelectedColor;
		}

		// Update the data grid body
		public function UpdateBody(pColumns:Array, pData:Array):void
		{
			// Calculate the required slider height
			var nRowHeight:Number = attributes.height / m_nVisibleRowCount;
			var nHeight:Number = nRowHeight * pData.length;
			if (nHeight < attributes.height)
			{
				nHeight = attributes.height;
			}
			
			// Force the height of the slider
			var pSlider:Form = _slider as Form;
			pSlider.ForceHeight(nHeight);
			doLayout();

			// Determine the hit areas for the table rows
			var pUpperLeftLocal:Point = new Point();
			var pLowerRightLocal:Point = new Point();
			var pUpperLeftGlobal:Point = new Point();
			var pLowerRightGlobal:Point = new Point();
			m_pHitAreasLocal = new Array();
			m_pHitAreasGlobal = new Array();
			var pHitAreaLocal:Rectangle, pHitAreaGlobal:Rectangle, nIndex:int, nOffset:Number = 0;
			for (nIndex = 0; nIndex < pData.length; ++nIndex)
			{
				pUpperLeftLocal.x = 0;
				pUpperLeftLocal.y = nOffset;
				pLowerRightLocal.x = pSlider.attributes.width;
				pLowerRightLocal.y = nOffset + nRowHeight;
				pHitAreaLocal = new Rectangle(pUpperLeftLocal.x, pUpperLeftLocal.y, pLowerRightLocal.x - pUpperLeftLocal.x,
					pLowerRightLocal.y - pUpperLeftLocal.y);
				m_pHitAreasLocal.push(pHitAreaLocal);
				pUpperLeftGlobal = localToGlobal(pUpperLeftLocal);
				pLowerRightGlobal = localToGlobal(pLowerRightLocal);
				pHitAreaGlobal = new Rectangle(pUpperLeftGlobal.x, pUpperLeftGlobal.y, pLowerRightGlobal.x - pUpperLeftGlobal.x,
					pLowerRightGlobal.y - pUpperLeftGlobal.y);
				m_pHitAreasGlobal.push(pHitAreaGlobal);
				nOffset += nRowHeight;
			}

			// Calculate the width of each column
			m_pColumnWidths = new Array();
			var pColumn:Column;
			for each (pColumn in pColumns)
			{
				m_pColumnWidths.push(pSlider.attributes.width * pColumn.PercentWidth / 100);
			}
			
			// Adjust the number of labels to match the number of rows and columns
			var pLabels:Array, pLabel:UILabel, nRowIndex:int, nColumnIndex:int;
			for (nRowIndex = 0; nRowIndex < pData.length; ++nRowIndex)
			{
				// Check if the row exists
				if (nRowIndex < m_pLabels.length)
				{
					// Adjust the number of columns on the existing row
					pLabels = m_pLabels[nRowIndex] as Array;
					while (pLabels.length < pColumns.length)
					{
						pLabels.push(AddLabel());
					}
					while (pLabels.length > pColumns.length)
					{
						pLabel = pLabels.pop();
						removeChild(pLabel);
					}
				}
				else
				{
					// Add a new row
					pLabels = new Array();
					while (pLabels.length < pColumns.length)
					{
						pLabels.push(AddLabel());
					}
					m_pLabels.push(pLabels);
				}
			}
			while (m_pLabels.length > pData.length)
			{
				pLabels = m_pLabels.pop();
				while (pLabels.length)
				{
					pLabel = pLabels.pop();
					removeChild(pLabel);
				}
			}
			
			// Set our references and render
			m_pColumns = pColumns;
			m_pData = pData;
			Render();
		}

		// Render the component on the slider surface
		protected function Render():void
		{
			// Clear the slider surface and fill the background
			var pSlider:Form = _slider as Form;
			pSlider.graphics.clear();
			pSlider.graphics.beginFill(Styling.AS3Color(Styling.APPLICATION_BACKGROUND));
			pSlider.graphics.drawRect(0, 0, pSlider.attributes.width, pSlider.attributes.height);
			pSlider.graphics.endFill();
			
			// Draw the background of the selected row
			var pHitArea:Rectangle;
			if (m_nSelectedRow != -1)
			{
				pHitArea = m_pHitAreasLocal[m_nSelectedRow] as Rectangle;
				pSlider.graphics.beginFill(Styling.AS3Color(Styling.DATAGRID_SELECTED));
				pSlider.graphics.drawRect(pHitArea.x, pHitArea.y, pHitArea.width, pHitArea.height);
				pSlider.graphics.endFill();
			}
			
			// Draw the column dividers
			pSlider.graphics.lineStyle(DIVIDER_WIDTH, Styling.AS3Color(Styling.TEXT_GRAY4));
			var nOffset:Number = 0, nIndex:int;
			for (nIndex = 0; nIndex < (m_pColumns.length - 1); ++nIndex)
			{
				nOffset += m_pColumnWidths[nIndex];
				pSlider.graphics.moveTo(nOffset, 0);
				pSlider.graphics.lineTo(nOffset, pSlider.attributes.height);
			}
			
			// Draw the row dividers
			var nRowHeight:Number = attributes.height / m_nVisibleRowCount;
			nOffset = nRowHeight;
			while (nOffset < pSlider.attributes.height)
			{
				pSlider.graphics.moveTo(0, nOffset);
				pSlider.graphics.lineTo(pSlider.attributes.width, nOffset);
				nOffset += nRowHeight;
			}

			// Adjust the label contents and positions
			var nRowIndex:int, nColumnIndex:int, pColumn:Column, pLabel:UILabel, sFieldName:String;
			for (nRowIndex = 0; nRowIndex < m_pLabels.length; ++nRowIndex)
			{
				pHitArea = m_pHitAreasLocal[nRowIndex] as Rectangle;
				nOffset = pHitArea.x;
				for (nColumnIndex = 0; nColumnIndex < m_pColumns.length; ++nColumnIndex)
				{
					sFieldName = (m_pColumns[nColumnIndex] as Column).Data;
					pLabel = m_pLabels[nRowIndex][nColumnIndex] as UILabel;
					pLabel.text = FormatLabelText(m_pData[nRowIndex], sFieldName);
					pLabel.width = pLabel.textWidth + 5;
					pLabel.x = nOffset + DataGrid.TEXT_INDENT;
					pLabel.y = pHitArea.y + ((nRowHeight - pLabel.textHeight) / 2);
					nOffset += m_pColumnWidths[nColumnIndex];
				}
			}
		}

		// Create a new text label
		protected function AddLabel():UILabel
		{
			var pXML:XML =
				<label useEmbedded="true" alignH="left" alignV="bottom">
					<font face={m_sFontFace} size={m_nFontSize} />
				</label>;
			var pLabel:UILabel = (_slider as Form).CreateLabel(pXML, attributes);
			var pTextFormat:TextFormat = pLabel.getTextFormat();
			pTextFormat.align = TextFormatAlign.CENTER;
			pLabel.setTextFormat(pTextFormat);
			pLabel.textColor = m_nTextColor;
			pLabel.multiline = false;
			pLabel.wordWrap = false;
			return pLabel;
		}

		// Format the label text
		protected function FormatLabelText(pData:Object, sFieldName:String):String
		{
			// Split on ampersand
			var pFields:Array = sFieldName.split("&");
			
			// Format the return text
			var sLabelText:String = "", sField:String;
			for each (sField in pFields)
			{
				if (sLabelText != "")
				{
					sLabelText += " ";
				}
				sLabelText += pData[sField];
			}
			return sLabelText;
		}

		/***
		 * Member variables
		 **/
		
		// Datagrid XML
		protected static const DATAGRIDBODY:XML = 
			<frame />;

		// Parameters
		protected var m_sFontFace:String = "";
		protected var m_nFontSize:uint = 0;
		protected var m_nTextColor:uint = 0;
		protected var m_nVisibleRowCount:uint = 0;
		protected var m_nSelectedColor:uint = 0;

		// Column and data
		protected var m_pColumns:Array;
		protected var m_pColumnWidths:Array;
		protected var m_pData:Array;

		// Row hit areas
		protected var m_pHitAreasLocal:Array = new Array();
		protected var m_pHitAreasGlobal:Array = new Array();
		protected var m_nSelectedRow:int = -1;
		
		// Labels
		protected var m_pLabels:Array = new Array();

		// Constants
		protected static var DIVIDER_WIDTH:uint = 1;
	}
}
