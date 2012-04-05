package Elixys.Subviews
{
	import Elixys.Assets.*;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This subview baset is an extension of our extended Form class
	public class SubviewBase extends Form
	{
		/***
		 * Construction
		 **/
		
		public function SubviewBase(screen:Sprite, sMode:String, sSubviewType:String, pViewXML:XML, pEditXML:XML, 
									pRunXML:XML, attributes:Attributes)
		{
			// Remember the mode and subview type
			m_sMode = sMode;
			m_sSubviewType = sSubviewType;

			// Call the base constructor
			var pXML:XML;
			switch (m_sMode)
			{
				case Constants.VIEW:
					pXML = pViewXML;
					break;
				
				case Constants.EDIT:
					pXML = pEditXML;
					break;
				
				case Constants.RUN:
					pXML = pRunXML;
					break;
			}
			super(screen, pXML, attributes);
		}

		/***
		 * Member functions
		 **/
		
		// Updates the component
		public function UpdateComponent(pComponent:ComponentBase):void
		{
		}
		
		// Returns the subview type
		public function get SubviewType():String
		{
			return m_sSubviewType;
		}
		
		/***
		 * Member variables
		 **/

		// Mode and subview type
		protected var m_sMode:String;
		protected var m_sSubviewType:String;
	}
}
