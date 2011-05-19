package Elixys.Objects
{
	import Elixys.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class ClientDetailsHome extends JSONObject
	{
		// Constructor
		public function ClientDetailsHome(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type() != null) && (Type() != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Buttons():Array
		{
			// Parse the buttons
			if (m_pButtons == null)
			{
				m_pButtons = new Array();
				var pButtons:Array = super.flash_proxy::getProperty("buttons");
				for each (var pButtonObject:Object in pButtons)
				{
					var pButton:Button = new Button(null, pButtonObject);
					m_pButtons.push(pButton);
				}
			}
			return m_pButtons;
		}
		
		// Type
		static public var TYPE:String = "HOME";
		
		// State components
		private var m_pButtons:Array;
	}
}
