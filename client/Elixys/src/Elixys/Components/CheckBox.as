package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Events.CheckBoxEvent;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.MovieClip;
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.geom.Rectangle;
	
	// This check box component is an extension of our extended Form class
	public class CheckBox extends Form
	{
		/***
		 * Construction
		 **/
		
		public function CheckBox(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Call the base constructor
			var pAttributes:Attributes = attributes.copy();
			pAttributes.width = INITIAL_WIDTH;
			pAttributes.height = INITIAL_HEIGHT;
			super(screen, CHECKBOX, pAttributes);
			
			// Add the skins
			m_pCheckUpSkin = new checkbox_up() as MovieClip;
			addChild(m_pCheckUpSkin);
			m_pCheckDownSkin = new checkbox_down() as MovieClip;
			addChild(m_pCheckDownSkin);
			
			// Add event listener
			addEventListener(MouseEvent.MOUSE_DOWN, OnMouseDown);
		}

			
		/***
		 * Member functions
		 **/

		// Gets and sets the check box state
		public function get Checked():Boolean
		{
			return m_bChecked;
		}
		public function set Checked(value:Boolean):void
		{
			m_bChecked = value;
			Update();
		}

		protected function Update():void
		{
			// Set the skin dimensions
			m_pCheckUpSkin.width = m_pCheckDownSkin.width = CHECKBOX_SIZE / scaleX;
			m_pCheckUpSkin.height = m_pCheckDownSkin.height = CHECKBOX_SIZE / scaleY;
			
			// Set the skin position
			m_pCheckUpSkin.x = m_pCheckDownSkin.x = (attributes.width - m_pCheckUpSkin.width) / 2;
			m_pCheckUpSkin.y = m_pCheckDownSkin.y = (attributes.height - m_pCheckUpSkin.height) / 2;

			// Set the skin visibility
			m_pCheckUpSkin.visible = !m_bChecked;
			m_pCheckDownSkin.visible = m_bChecked;
			
			// Update the hit area
			var nHitToleranceX:Number = HIT_TOLERANCE / scaleX,
				nHitToleranceY:Number = HIT_TOLERANCE / scaleY;
			if (m_pCheckUpSkin.x > nHitToleranceX)
			{
				m_pHitArea.left = m_pCheckUpSkin.x - nHitToleranceX;
			}
			else
			{
				m_pHitArea.left = 0;
			}
			if (m_pCheckUpSkin.y > nHitToleranceY)
			{
				m_pHitArea.top = m_pCheckUpSkin.y - nHitToleranceY;
			}
			else
			{
				m_pHitArea.top = 0;
			}
			if ((m_pCheckUpSkin.x + m_pCheckUpSkin.width + nHitToleranceX) < attributes.width)
			{
				m_pHitArea.right = m_pCheckUpSkin.x + m_pCheckUpSkin.width + nHitToleranceX;
			}
			else
			{
				m_pHitArea.right = attributes.width;
			}
			if ((m_pCheckUpSkin.y + m_pCheckUpSkin.height + nHitToleranceY) < attributes.height)
			{
				m_pHitArea.bottom = m_pCheckUpSkin.y + m_pCheckUpSkin.height + nHitToleranceY;
			}
			else
			{
				m_pHitArea.bottom = attributes.height;
			}
		}
		
		// Called when the user clicks on the checkbox
		protected function OnMouseDown(event:MouseEvent):void
		{
			// Check if the user clicked in the hit area
			if (m_pHitArea.contains(mouseX, mouseY))
			{
				Checked = !Checked;
				dispatchEvent(new CheckBoxEvent(this));
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Checkbox component XML
		protected static const CHECKBOX:XML = 
			<frame alignH="fill" alignV="fill" background={Styling.APPLICATION_BACKGROUND} />;
		
		// Check skins
		protected var m_pCheckUpSkin:MovieClip;
		protected var m_pCheckDownSkin:MovieClip;
		
		// Checked flag
		protected var m_bChecked:Boolean = false;
		
		// Hit area
		protected var m_pHitArea:Rectangle = new Rectangle();
		
		// Checkbox size and hit tolerance
		protected static const CHECKBOX_SIZE:int = 25;
		protected static const HIT_TOLERANCE:int = 15;
		protected static const INITIAL_WIDTH:int = 200;
		protected static const INITIAL_HEIGHT:int = 60;

	}
}
