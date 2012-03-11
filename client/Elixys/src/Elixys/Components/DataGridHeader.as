package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.ButtonEvent;
	import Elixys.Extended.Form;
	import Elixys.JSON.State.Column;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Sprite;
	import flash.events.MouseEvent;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	import flash.utils.*;
	
	// This data grid header component is an extension of the Form class
	public class DataGridHeader extends Form
	{
		/***
		 * Construction
		 **/
		
		public function DataGridHeader(screen:Sprite, xml:XML, attributes:Attributes = null, row:Boolean = false, inGroup:Boolean = false)
		{
			// Call the base constructor
			super(screen, DATAGRIDHEADER, attributes);
			
			// Add event listeners
			addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
		}

		/***
		 * Member functions
		 **/
		
		// Set data grid header parameters
		public function SetParameters(sFontFace:String, nFontSize:uint, nTextColor:uint, nPressedColor:uint,
									  sSortUpSkin:String, sSortDownSkin:String):void
		{
			m_sFontFace = sFontFace;
			m_nFontSize = nFontSize;
			m_nTextColor = nTextColor;
			m_nPressedColor = nPressedColor;
			m_sSortUpSkin = sSortUpSkin;
			m_sSortDownSkin = sSortDownSkin;
			m_pSortUpSkinClass = getDefinitionByName(m_sSortUpSkin) as Class;
			m_pSortDownSkinClass = getDefinitionByName(m_sSortDownSkin) as Class;
		}

		// Update the data grid headers
		public function UpdateHeader(pColumns:Array):void
		{
			// Determine the hit areas for the table headers
			var pUpperLeftLocal:Point = new Point();
			var pLowerRightLocal:Point = new Point();
			var pUpperLeftGlobal:Point = new Point();
			var pLowerRightGlobal:Point = new Point();
			m_pHitAreasLocal = new Array();
			m_pHitAreasGlobal = new Array();
			var pHitAreaLocal:Rectangle, pHitAreaGlobal:Rectangle, pColumn:Column, nOffset:int = 0, nWidth:int;
			for each (pColumn in pColumns)
			{
				nWidth = attributes.width * pColumn.PercentWidth / 100;
				pUpperLeftLocal.x = nOffset;
				pUpperLeftLocal.y = 0;
				pLowerRightLocal.x = nOffset + nWidth;
				pLowerRightLocal.y = attributes.height;
				pHitAreaLocal = new Rectangle(pUpperLeftLocal.x, pUpperLeftLocal.y, pLowerRightLocal.x - pUpperLeftLocal.x,
					pLowerRightLocal.y - pUpperLeftLocal.y);
				m_pHitAreasLocal.push(pHitAreaLocal);
				pUpperLeftGlobal = localToGlobal(pUpperLeftLocal);
				pLowerRightGlobal = localToGlobal(pLowerRightLocal);
				pHitAreaGlobal = new Rectangle(pUpperLeftGlobal.x, pUpperLeftGlobal.y, pLowerRightGlobal.x - pUpperLeftGlobal.x,
					pLowerRightGlobal.y - pUpperLeftGlobal.y);
				m_pHitAreasGlobal.push(pHitAreaGlobal);
				nOffset += nWidth;
			}
			
			// Adjust the number of labels to match the number of columns
			var pLabel:UILabel;
			if (m_pLabels.length != pColumns.length)
			{
				while (m_pLabels.length < pColumns.length)
				{
					var pXML:XML =
						<label useEmbedded="true" alignH="left" alignV="bottom">
							<font face={m_sFontFace} size={m_nFontSize} />
						</label>;
					pLabel = CreateLabel(pXML, attributes);
					var pTextFormat:TextFormat = pLabel.getTextFormat();
					pTextFormat.align = TextFormatAlign.CENTER;
					pLabel.setTextFormat(pTextFormat);
					pLabel.textColor = m_nTextColor;
					m_pLabels.push(pLabel);
				}
				while (m_pLabels.length > pColumns.length)
				{
					pLabel = m_pLabels.pop();
					removeChild(pLabel);
				}
			}
			
			// Update the sort icons
			var nIndex:int, pSortIcon:MovieClip;
			for (nIndex = 0; nIndex < pColumns.length; ++nIndex)
			{
				// Continue if we already have the correct sort icon
				pColumn = pColumns[nIndex] as Column;
				if (m_pSortIcons.length > nIndex)
				{
					if (!pColumn.Sortable)
					{
						if (m_pSortIcons[nIndex] == null)
						{
							continue;
						}
					}
					else
					{
						if (pColumn.SortMode == "up")
						{
							if (getQualifiedClassName(m_pSortIcons[nIndex]) == getQualifiedClassName(m_pSortUpSkinClass))
							{
								continue;
							}
						}
						else if (pColumn.SortMode == "down")
						{
							if (getQualifiedClassName(m_pSortIcons[nIndex]) == getQualifiedClassName(m_pSortDownSkinClass))
							{
								continue;
							}
						}
						else
						{
							if (m_pSortIcons[nIndex] == null)
							{
								continue;
							}
						}
					}
				}
				
				// Remove any existing sort icon
				if ((nIndex < m_pSortIcons.length) && (m_pSortIcons[nIndex] != null))
				{
					removeChild(m_pSortIcons[nIndex]);
					m_pSortIcons[nIndex] = null;
				}
				
				// Add the appropriate sort icon
				pSortIcon = null;
				if (pColumn.Sortable)
				{
					if (pColumn.SortMode == "up")
					{
						pSortIcon = new m_pSortUpSkinClass() as MovieClip;
						addChild(pSortIcon);
					}
					else if (pColumn.SortMode == "down")
					{
						pSortIcon = new m_pSortDownSkinClass() as MovieClip;
						addChild(pSortIcon);
					}
				}
				if (nIndex < m_pSortIcons.length)
				{
					m_pSortIcons[nIndex] = pSortIcon
				}
				else
				{
					m_pSortIcons.push(pSortIcon);
				}
			}
			
			// Set our columns reference and render
			m_pColumns = pColumns;
			Render();
		}
		
		// Render the component
		protected function Render():void
		{
			// Adjust the labels and icons
			var nIndex:int, pColumn:Column, pLabel:UILabel, pHitArea:Rectangle, pSortIcon:MovieClip;
			for (nIndex = 0; nIndex < m_pColumns.length; ++nIndex)
			{
				pColumn = m_pColumns[nIndex] as Column;
				pLabel = m_pLabels[nIndex] as UILabel;
				pHitArea = m_pHitAreasLocal[nIndex] as Rectangle;
				pLabel.text = pColumn.Display;
				pLabel.x = pHitArea.x + DataGrid.TEXT_INDENT;
				pLabel.y = (attributes.height - pLabel.textHeight) / 2;
				if (m_pSortIcons[nIndex] != null)
				{
					pSortIcon = m_pSortIcons[nIndex] as MovieClip;
					pSortIcon.x = pHitArea.right - LABEL_INDENT - pSortIcon.width;
					pSortIcon.y = (attributes.height - pSortIcon.height) / 2;
				}
			}

			// Paint our background to define the area where we will receive mouse down events
			graphics.clear();
			graphics.beginFill(Styling.AS3Color(Styling.APPLICATION_BACKGROUND));
			graphics.drawRect(0, 0, attributes.width, attributes.height);
			graphics.endFill();

			// Draw the column dividers
			graphics.lineStyle(DIVIDER_WIDTH, Styling.AS3Color(Styling.DATAGRID_HEADERLINE));
			for (nIndex = 0; nIndex < (m_pHitAreasLocal.length - 1); ++nIndex)
			{
				pHitArea = m_pHitAreasLocal[nIndex] as Rectangle;
				graphics.moveTo(pHitArea.right, pHitArea.y + DIVIDER_GAP);
				graphics.lineTo(pHitArea.right, pHitArea.bottom - DIVIDER_GAP);
			}

			// Draw the background of the pressed header
			if (m_nPressedHeader != -1)
			{
				pHitArea = m_pHitAreasLocal[m_nPressedHeader] as Rectangle;
				var nX:Number = pHitArea.x + DIVIDER_WIDTH + HEADERPRESSED_GAP;
				var nY:Number = pHitArea.y + HEADERPRESSED_GAP;
				var nWidth:Number = pHitArea.width - (HEADERPRESSED_GAP * 2) - (DIVIDER_WIDTH * 2);
				var nHeight:Number = pHitArea.height - (HEADERPRESSED_GAP * 2) - DIVIDER_WIDTH;
				graphics.beginFill(Styling.AS3Color(Styling.DATAGRID_HEADERPRESSED));
				graphics.drawRoundRect(nX, nY, nWidth, nHeight, HEADERPRESSED_CURVE, HEADERPRESSED_CURVE);
				graphics.endFill();
			}
		}

		// Called when the user presses the mouse button
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Check for a header click
			for (var nIndex:int = 0; nIndex < m_pHitAreasGlobal.length; ++nIndex)
			{
				// Ignore hits to columns that are not sortable
				if (!(m_pColumns[nIndex] as Column).Sortable)
				{
					continue;
				}
				
				// Hit test
				if ((m_pHitAreasGlobal[nIndex] as Rectangle).contains(event.stageX, event.stageY))
				{
					// Listen for mouse up
					stage.addEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
					
					// Set the pressed header index and render
					m_nPressedHeader = nIndex;
					Render();
					break;
				}
			}
		}
		
		// Called when the user releases the mouse button
		protected function OnMouseUp(event:MouseEvent):void
		{
			// Remove the event listener
			stage.removeEventListener(MouseEvent.MOUSE_UP, OnMouseUp);
			
			// Check if the mouse was released over the pressed header
			if ((m_pHitAreasGlobal[m_nPressedHeader] as Rectangle).contains(event.stageX, event.stageY))
			{
				// Dispatch a click event
				dispatchEvent(new ButtonEvent((m_pColumns[m_nPressedHeader] as Column).Data));
			}
			
			// Release the header and render
			m_nPressedHeader = -1;
			Render();
		}
		
		/***
		 * Member variables
		 **/
		
		// Datagrid header XML
		protected static const DATAGRIDHEADER:XML = 
			<frame />;

		// Parameters
		protected var m_sFontFace:String = "";
		protected var m_nFontSize:uint = 0;
		protected var m_nTextColor:uint = 0;
		protected var m_nPressedColor:uint = 0;
		protected var m_sSortUpSkin:String = "";
		protected var m_sSortDownSkin:String = "";
		protected var m_pSortUpSkinClass:Class;
		protected var m_pSortDownSkinClass:Class;

		// Columns
		protected var m_pColumns:Array;
		
		// Header hit areas
		protected var m_pHitAreasLocal:Array = new Array();
		protected var m_pHitAreasGlobal:Array = new Array();
		protected var m_nPressedHeader:int = -1;

		// Labels and sort icons
		protected var m_pLabels:Array = new Array();
		protected var m_pSortIcons:Array = new Array();
		
		// Constants
		protected static var DIVIDER_WIDTH:uint = 2;
		protected static var DIVIDER_GAP:uint = 8;
		protected static var LABEL_INDENT:uint = 15;
		protected static var HEADERPRESSED_GAP:int = 1;
		protected static var HEADERPRESSED_CURVE:int = 8;
	}
}
