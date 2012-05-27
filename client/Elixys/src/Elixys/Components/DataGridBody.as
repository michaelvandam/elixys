package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.SelectionEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Column;
	import Elixys.JSON.State.SequenceMetadata;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextField;
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
			
			// Call the base implementation
			super.layout(attributes);
		}

		// Override the hit searching function
		protected override function doSearchHit():void
		{
			// Convert from local to global coordinates
			var pLocalPoint:Point = new Point(_slider.mouseX, _slider.mouseY);
			var pGlobalPoint:Point = _slider.localToGlobal(pLocalPoint);

			// Check for a row click
			for (var nIndex:int = 0; nIndex < m_pHitAreas.length; ++nIndex)
			{
				if ((m_pHitAreas[nIndex] as Rectangle).contains(_slider.mouseX, _slider.mouseY))
				{
					// Dispatch a selection change event, set the selected row index and render
					dispatchEvent(new SelectionEvent(m_pData[nIndex][m_sIDField]));
					m_nSelectedRow = nIndex;
					Render();
					return;
				}
			}
		}

		// Set data grid header parameters
		public function SetParameters(sFontFace:String, nFontSize:uint, nTextColor:uint, nTextSelectedColor:uint,
									  nVisibleRowCount:uint, nSelectedColor:uint, nIDField:String):void
		{
			m_sFontFace = sFontFace;
			m_nFontSize = nFontSize;
			m_nTextColor = nTextColor;
			m_nTextSelectedColor = nTextSelectedColor;
			m_nVisibleRowCount = nVisibleRowCount;
			m_nSelectedColor = nSelectedColor;
			m_sIDField = nIDField;
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
			var pUpperLeft:Point = new Point();
			var pLowerRight:Point = new Point();
			m_pHitAreas = new Array();
			var pHitArea:Rectangle, nIndex:int, nOffset:Number = 0;
			for (nIndex = 0; nIndex < pData.length; ++nIndex)
			{
				pUpperLeft.x = 0;
				pUpperLeft.y = nOffset;
				pLowerRight.x = pSlider.attributes.width;
				pLowerRight.y = nOffset + nRowHeight;
				pHitArea = new Rectangle(pUpperLeft.x, pUpperLeft.y, pLowerRight.x - pUpperLeft.x, pLowerRight.y - pUpperLeft.y);
				m_pHitAreas.push(pHitArea);
				nOffset += nRowHeight;
			}

			// Calculate the width of each column
			m_pColumnWidths = new Array();
			var pColumn:Column;
			for each (pColumn in pColumns)
			{
				m_pColumnWidths.push(pSlider.attributes.width * pColumn.PercentWidth / 100);
			}
			
			// Adjust the actual number of labels and warning icons
			var pLabels:Array, pLabel:UILabel, pWarningIcon:Sprite, nRowIndex:int, nColumnIndex:int;
			for (nRowIndex = 0; nRowIndex < pData.length; ++nRowIndex)
			{
				// Check if the label row exists
				if (nRowIndex < m_pLabels.length)
				{
					// Adjust the number of columns on the existing row
					pLabels = m_pLabels[nRowIndex] as Array;
					while (pLabels.length < pColumns.length)
					{
						pLabels.push(Utils.AddLabel("", _slider as Form, m_sFontFace, m_nFontSize, m_nTextColor));
					}
					while (pLabels.length > pColumns.length)
					{
						pLabel = pLabels.pop();
						_slider.removeChild(pLabel);
					}
				}
				else
				{
					// Add a new row
					pLabels = new Array();
					while (pLabels.length < pColumns.length)
					{
						pLabels.push(Utils.AddLabel("", _slider as Form, m_sFontFace, m_nFontSize, m_nTextColor));
					}
					m_pLabels.push(pLabels);
				}
				
				// Add warning icons as needed
				if (nRowIndex >= m_pWarningIcons.length)
				{
					pWarningIcon = Utils.AddSkin(warningIcon_up, true, _slider, 0, nRowHeight * WARNING_ICON_PERCENT / 100);
					m_pWarningIcons.push(pWarningIcon);
				}
			}
			while (m_pLabels.length > pData.length)
			{
				pLabels = m_pLabels.pop();
				while (pLabels.length)
				{
					pLabel = pLabels.pop();
					_slider.removeChild(pLabel);
				}
			}
			while (m_pWarningIcons.length > pData.length)
			{
				pWarningIcon = m_pWarningIcons.pop();
				_slider.removeChild(pWarningIcon);
			}
			
			// Update the current selection
			if (m_nSelectedRow != -1)
			{
				for (nRowIndex = 0; nRowIndex < pData.length; ++nRowIndex)
				{
					if (pData[nRowIndex][m_sIDField] == SelectionID)
					{
						m_nSelectedRow = nRowIndex;
						break;
					}
				}
				if (nRowIndex == pData.length)
				{
					m_nSelectedRow = -1;
					dispatchEvent(new SelectionEvent(-1));
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
				pHitArea = m_pHitAreas[m_nSelectedRow] as Rectangle;
				pSlider.graphics.beginFill(Styling.AS3Color(Styling.DATAGRID_SELECTED));
				pSlider.graphics.drawRect(pHitArea.x, pHitArea.y, pHitArea.width, pHitArea.height);
				pSlider.graphics.endFill();
			}
			
			// Draw the column dividers
			pSlider.graphics.lineStyle(DIVIDER_WIDTH, Styling.AS3Color(Styling.TEXT_GRAY5));
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

			// Adjust the labels and warning icons
			var nRowIndex:int, nColumnIndex:int, pColumn:Column, pLabel:UILabel, pWarningIcon:Sprite,
				sFieldName:String;
			for (nRowIndex = 0; nRowIndex < m_pLabels.length; ++nRowIndex)
			{
				// Adjust the warning icons visibility and positions
				pHitArea = m_pHitAreas[nRowIndex] as Rectangle;
				pWarningIcon = m_pWarningIcons[nRowIndex] as Sprite;
				if ((m_pData[nRowIndex] as SequenceMetadata).Valid)
				{
					pWarningIcon.visible = false;
				}
				else
				{
					pWarningIcon.visible = true;
					pWarningIcon.x = m_pColumnWidths[0] - pWarningIcon.width - DataGrid.TEXT_INDENT;
					pWarningIcon.y = pHitArea.y + ((pHitArea.height - pWarningIcon.height) / 2) + WARNING_ICON_OFFSET;
				}

				// Adjust the label contents and positions
				nOffset = pHitArea.x;
				for (nColumnIndex = 0; nColumnIndex < m_pColumns.length; ++nColumnIndex)
				{
					sFieldName = (m_pColumns[nColumnIndex] as Column).Data;
					pLabel = m_pLabels[nRowIndex][nColumnIndex] as UILabel;
					pLabel.text = FormatLabelText(m_pData[nRowIndex], sFieldName);
					if (nRowIndex == m_nSelectedRow)
					{
						pLabel.textColor = m_nTextSelectedColor;
					}
					else
					{
						pLabel.textColor = m_nTextColor;
					}
					var nColumnWidth:Number = m_pColumnWidths[nColumnIndex] - (DataGrid.TEXT_INDENT * 2);
					if ((nColumnIndex == 0) && !(m_pData[nRowIndex] as SequenceMetadata).Valid)
					{
						nColumnWidth -= pWarningIcon.width + (DataGrid.TEXT_INDENT / 2);
					}
					if (pLabel.textWidth < nColumnWidth)
					{
						pLabel.width = pLabel.textWidth + 5;
					}
					else
					{
						AddEllipsis(pLabel, nColumnWidth);
					}
					pLabel.x = nOffset + DataGrid.TEXT_INDENT;
					pLabel.y = pHitArea.y + ((nRowHeight - pLabel.textHeight) / 2);
					nOffset += m_pColumnWidths[nColumnIndex];
				}
			}
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

		// Reduces the string width and adds ellipsis
		protected function AddEllipsis(pTextField:TextField, nMaxWidth:int):void
		{
			if (pTextField.textWidth > nMaxWidth)
			{
				// Append the ellipsis
				pTextField.appendText("...");
				
				// Loop until the string is small enough
				while (pTextField.textWidth > nMaxWidth)
				{
					pTextField.replaceText(pTextField.text.length - 4, pTextField.text.length - 3, "");
				}
			}
		}

		// Returns the ID of the selected item
		public function get SelectionID():int
		{
			if (m_nSelectedRow != -1)
			{
				return m_pData[m_nSelectedRow][m_sIDField];
			}
			else
			{
				return -1;
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Datagrid XML
		protected static const DATAGRIDBODY:XML = 
			<frame border="false" />;

		// Parameters
		protected var m_sFontFace:String = "";
		protected var m_nFontSize:uint = 0;
		protected var m_nTextColor:uint = 0;
		protected var m_nTextSelectedColor:uint = 0;
		protected var m_nVisibleRowCount:uint = 0;
		protected var m_nSelectedColor:uint = 0;
		protected var m_sIDField:String = "";

		// Column and data
		protected var m_pColumns:Array;
		protected var m_pColumnWidths:Array;
		protected var m_pData:Array;

		// Row hit areas
		protected var m_pHitAreas:Array = new Array();
		protected var m_nSelectedRow:int = -1;
		
		// Labels and warning icons
		protected var m_pLabels:Array = new Array();
		protected var m_pWarningIcons:Array = new Array();

		// Constants
		protected static var DIVIDER_WIDTH:uint = 1;
		protected static var WARNING_ICON_PERCENT:int = 45;
		protected static var WARNING_ICON_OFFSET:int = 3;
	}
}
